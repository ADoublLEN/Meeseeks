import re


from source.model.base_model import BaseModel
from source.prompt_templates.coding_extractor import EXTRACTION_PROMPT_BY_CODING
from source.prompt_templates.coding_extractor_single import EXTRACTION_PROMPT_BY_CODING_SINGLE
from source.prompt_templates.general_evaluator import EVALUATION_PROMPT
from source.prompt_templates.general_extractor_multi import EXTRACTION_PROMPT_MULTI
from source.prompt_templates.general_extractor_single import EXTRACTION_PROMPT_SINGLE
from source.tools.process_corresponding_parts import extract_by_coding
from source.tools.process_evaluation import collect_questions_by_level
from source.tools.process_rule_based_evaluate import rule_based_evaluate
from source.tools.utils import txt_to_json, get_json_info_by_key


class MeeseeksBaseFramework():
    """
    Base class that implements the basic functions of Meeseeks Evalutaion.
    """
    def __init__(self, target_model: BaseModel, extract_model: BaseModel, score_model:BaseModel):
        self.target_model = target_model
        self.extract_model = extract_model
        self.score_model = score_model
    async def inference(self, data):
        """
        Call the target model to generate a single round response
        :param data:
        :return:
        """

        return await self.target_model.generate(data)



    async def extract(self, data):
        """
        Call Extraction Model to extract target info from the response
        :return:
        """

        # init extraction_results
        for i in range(len(data)):
            if "corresponding_parts" in data:
                data["extraction_results"] = data["corresponding_parts"].copy()
            else:
                return data

        print(f"Extract Content Start, data: {data}")

        # prepare different types of prompts.
        coding_prompts, coding_keys = [], []
        normal_prompts, normal_keys = [], []
        json_keys = []

        # traverse all parts
        for key, extraction_prompt in data["corresponding_parts"].items():
            if "#CODE#" in extraction_prompt:
                # process code type
                prompt = (EXTRACTION_PROMPT_BY_CODING_SINGLE if "single" in data["category"]
                          else EXTRACTION_PROMPT_BY_CODING).format(
                    model_response=data["model_response"].replace("\n", ""),
                    instruction=extraction_prompt.replace("#CODE#", "")
                )
                coding_prompts.append(prompt)
                coding_keys.append(key)

            elif "#JSONSCHEMA#" in extraction_prompt:
                # process json type
                json_keys.append(key)

            elif not "#LISTSCHEMA#" in extraction_prompt:
                # process plain text type
                prompt = (EXTRACTION_PROMPT_SINGLE if "single" in data["category"]
                          else EXTRACTION_PROMPT_MULTI).format(
                    input_instruction=data["question"],
                    model_response=data["model_response"],
                    extraction_prompt=extraction_prompt
                )
                normal_prompts.append(prompt)
                normal_keys.append(key)

        # process coding prompts
        if coding_prompts:
            try:
                request_data = [[{
                    "role": "user",
                    "content":p}] for p in coding_prompts]
                results = [await self.extract_model.generate(request) for request in request_data]
                coding_results = [extract_by_coding(res, data["model_response"])
                                  for res in results]

                for key, result in zip(coding_keys, coding_results):
                    data["extraction_results"][key] = result

            except Exception as e:
                print(f"Coding extraction failed: {repr(e)}")
                for key in coding_keys:
                    data["extraction_results"][key] = None

        # process normal prompts
        if normal_prompts:
            request_data = [[{
                "role": "user",
                "content": p}] for p in normal_prompts]
            results = [await self.extract_model.generate(request) for request in request_data]

            for key, result in zip(normal_keys, results):
                try:
                    parsed = txt_to_json(result)
                    data["extraction_results"][key] = (
                        data["model_response"] if parsed == "ALL" else parsed
                    )
                except Exception as e:
                    print(f"Normal extraction failed: {e}")
                    data["extraction_results"][key] = "INVALID"

        # process json prompts
        for key in json_keys:
            try:
                data["extraction_results"][key] = [
                    str(get_json_info_by_key(
                        data["model_response"],
                        data["extraction_results"][key]
                    ))
                ]
            except Exception:
                data["extraction_results"][key] = "INVALID"

        return data


    async def score(self, items):
        """
        Call Score Model to score the target info based on givin rules.
        :return:
        """
        questions_by_level = collect_questions_by_level(items)
        max_level = max(questions_by_level.keys())

        # save original item references
        original_items = {id(item): item for item in items}

        # process each level of questions
        for level in range(max_level + 1):
            print(f"\nProcessing level {level} questions...")
            level_questions = questions_by_level[level]
            processed_count = 0
            print(f"level_questions: {level_questions}")
            if level != 0:
                print(f"last_level_({level - 1})questions: {questions_by_level[level - 1]}")

            # process questions from current level
            for i in range(0, len(level_questions), 1):
                batch = level_questions[i:i + 1]
                valid_batch = []
                # check dependencies
                for sub_q in batch:
                    if level == 0 or self.check_dependencies(sub_q, sub_q["_item"]):
                        valid_batch.append(sub_q)
                    else:
                        sub_q["eval_result"] = 0
                        sub_q["eval_explanation"] = "Dependencies failed"
                        sub_q["eval_method"] = "dependency check"
                        processed_count += 1
                        print(f"Question {sub_q} marked as failed due to dependencies")

                # 处理有效的批次
                # 修改调用方式
                if valid_batch:
                    non_rule_batch = [sub_q for sub_q in valid_batch if sub_q.get("rule") is None]
                    rule_batch = [sub_q for sub_q in valid_batch if sub_q.get("rule") is not None]
                    if rule_batch:
                        await self.get_mixed_evaluation(rule_batch)
                    if non_rule_batch:
                        await self.model_evaluation(non_rule_batch)
                processed_count += len(valid_batch)
                print(f"Processed {processed_count}/{len(level_questions)} level {level} questions")

            # update refs for rest level items after processing current level
            if level < max_level:
                for next_level in range(level + 1, max_level + 1):
                    for sub_q in questions_by_level[next_level]:
                        item_id = id(sub_q["_item"])
                        sub_q["_item"] = original_items[item_id]


        for item in items:
            for sub_q in item["sub_questions"]:
                if "_item" in sub_q:
                    del sub_q["_item"]
                if sub_q["rule"] == "SCHEMA:json_schema":
                    item["sub_questions"] = sub_q["eval_result"] + item["sub_questions"][1:]

        print("\nProcessing completed!")
        return items


    def check_dependencies(self, sub_question, full_subq_res):
        for sub_q in full_subq_res["sub_questions"]:
            if sub_q["point_id"] in sub_question["dep"]:
                if sub_q["eval_result"] == 0:
                    return False
        return True

    async def get_mixed_evaluation(self, sub_questions):
        for sub_q in sub_questions:
            item = sub_q["_item"]
            if sub_q['rule'].startswith("SCHEMA"):
                sub_q["eval_result"] = rule_based_evaluate(
                    item,
                    sub_q["rule"],
                    item["model_response"]
                )
            else:
                corresponding_part = item["extraction_results"][sub_q["corresponding_part"]]
                if corresponding_part == "INVALID":
                    sub_q["eval_result"] = 0
                    sub_q['eval_explanation'] = "MODEL ERROR"
                else:
                    sub_q["eval_result"], sub_q['eval_explanation'] = rule_based_evaluate(
                        item,
                        sub_q["rule"],
                        corresponding_part
                    )

                sub_q["eval_method"] = "rule evaluation"
        return sub_questions

    async def model_evaluation(self, sub_questions):
        # prepare prompt for each sub question
        prompts = [EVALUATION_PROMPT.format(
            input=sub_q['_item']["question"],
            output=sub_q['_item']["model_response"],
            question=sub_q["question"]
        ) for sub_q in sub_questions]

        # query score model
        request_data =[[{"role": "user", "content": prompt}] for prompt in prompts]
        raw_results = [await self.score_model.generate(request) for request in request_data]

        # process each result
        for sub_question, raw_res in zip(sub_questions, raw_results):
            try:
                re_result = re.findall(r'判断：是|判断：否', raw_res)
                if "是" in re_result[0]:
                    sub_question["eval_result"] = 1
                else:
                    sub_question["eval_result"] = 0
                sub_question["eval_explanation"] = raw_res
            except Exception as e:
                sub_question["eval_result"] = 0
                sub_question["eval_explanation"] = str(e)
            sub_question["eval_method"] = "pure model evaluation"

        return sub_questions