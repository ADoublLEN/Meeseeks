import asyncio
import copy
import json
import os
import traceback
from datetime import datetime

from tqdm import tqdm

from .meeseeks_base_framework import MeeseeksBaseFramework
from source.model.base_model import BaseModel
from ..tools.hierarchical_relationship import hierarchical_relationship


class MeeseeksMultiTurnFramework(MeeseeksBaseFramework):

    def __init__(self, target_model: BaseModel, extract_model: BaseModel, score_model:BaseModel, data_path, total_rounds=3,concurrency=50):
        super().__init__(target_model, extract_model, score_model)
        self.data = json.load(open(data_path, "r"))
        self.data = self.data
        self.total_rounds = total_rounds
        self.concurrency = concurrency


    async def run(self):
        tasks = [self.run_one(data) for data in self.data]
        sem = asyncio.Semaphore(self.concurrency)
        async def wrapped_task(task):
            async with sem:
                return await task
        tasks = [wrapped_task(task) for task in tasks]

        # parallel process each item
        multi_turn_request_list = []
        multi_turn_result_list = []
        model_score_result_list = []
        extracted_content_list = []

        print(f"loaded {len(tasks)} items, start processing...", flush=True)

        with tqdm(total=len(tasks), desc="Processing Items") as pbar:
            for coro in asyncio.as_completed(tasks):
                try:
                    multi_turn_requests, multi_turn_results, model_score_result, extracted_content = await coro
                    model_score_result_list.append(model_score_result)
                    multi_turn_request_list.append(multi_turn_requests)
                    multi_turn_result_list.append(multi_turn_results)
                    extracted_content_list.append(extracted_content)
                except Exception as e:
                    print(f"Generated an exception: {repr(e)}", flush=True)
                    print(traceback.format_exc(), flush=True)
                pbar.update(1)


        print(f"Evaludation Finished, start summarizing...")

        # summarize
        self.summarize(model_score_result_list, multi_turn_request_list, multi_turn_result_list, extracted_content_list)

    async def run_one(self, data):

        conv = []
        multi_turn_results = []
        extracted_content_list = []
        model_score_result = []
        multi_turn_requests = []

        for round in range(self.total_rounds):
            if round == 0:
                conv.append({'role':'user', 'content': data['question']})
            # get response
            response_text = await self.inference(conv)
            # record request and result
            multi_turn_requests.append(copy.deepcopy(conv))
            multi_turn_results.append(response_text)

            # update conv
            conv.append({'role':'assistant', 'content': response_text})
            detail_batch_info = copy.deepcopy(data)
            detail_batch_info['model_response'] = response_text

            # extract
            extracted_content = await self.extract(detail_batch_info)
            extracted_content_list.append(extracted_content)


            score_result = await self.score([extracted_content])


            # calculate final score for this round
            final_score, strict_final_score, scorepts_catch_condition = self.model_eval_score(score_result[0])
            score_result[0]["final_score"] = final_score
            score_result[0]["strict_final_score"] = strict_final_score
            score_result[0]["scorepts_catch_condition"] = scorepts_catch_condition
            # save result
            model_score_result.append(score_result[0])

            # check if we need to break
            if final_score == 1:
                break
            # if not, build new prompt for next rond
            next_prompt = "你的回答中存在以下问题\n"
            for subq in score_result[0]["sub_questions"]:
                if subq["eval_result"] == 0:
                    next_prompt += f"{subq['question']}未满足，未满足的具体信息：{subq['eval_explanation']}\n"
            next_prompt += "请根据这些信息给出你修正后的回答，注意：只输出回答，不要输出额外信息。"
            conv.append({'role':'user', 'content': next_prompt})

        return multi_turn_requests, multi_turn_results, model_score_result, extracted_content_list

    def model_eval_score(self, res):
        subqs = res["sub_questions"]
        final_score, strict_final_score = self.calculate_final_score(subqs)
        res["final_score"] = final_score
        scorepts_catch_condition = [score['eval_result'] for score in subqs]
        return final_score, strict_final_score, scorepts_catch_condition

    def calculate_final_score(self, subqs):
        capabilities = {}
        for sub_q in subqs:
            if "能力项" not in sub_q:
                continue
            if sub_q["能力项"] not in capabilities:
                capabilities[sub_q["能力项"]] = []
            capabilities[sub_q["能力项"]].append(sub_q["eval_result"])

        print(f"capabilities: {capabilities}")
        score_by_capability = 0
        for capability, scores in capabilities.items():
            score_by_capability += sum(scores) / len(scores)

        if len(capabilities) == 0:
            score_by_capability = 0  # 肯定哪里出问题了
        else:
            score_by_capability = score_by_capability / len(capabilities)

        strict_cur_score = 0 if score_by_capability < 1 else score_by_capability
        return score_by_capability, strict_cur_score
    def summarize(self, model_score_result_list,  multi_turn_request_list, multi_turn_result_list, extracted_content_list):
        score_dict = {}
        # print(f"model score result list: \n{model_score_result_list}")
        total = len(model_score_result_list)
        # Final Scores
        sum_meeseeks_score = sum([x[-1]['final_score'] for x in model_score_result_list]) # use the score of the last round of each item
        avg_meeseeks_score = sum_meeseeks_score / total if total != 0 else 0
        sum_ultility_score = sum([x[-1]['strict_final_score'] for x in model_score_result_list])
        avg_ultility_score = sum_ultility_score / total if total != 0 else 0
        score_dict["meeseeks_score"] = avg_meeseeks_score
        score_dict["ultility_score"] = avg_ultility_score
        print("=" * 30)
        print(f"Final Meeseeks Score: {avg_meeseeks_score}", flush=True)
        print(f"Final Utility Rate: {avg_ultility_score}", flush=True)
        print("=" * 30)
        # Score for each round
        for i in range(self.total_rounds):
            round_scores =[]
            round_strict_scores = []
            for item in model_score_result_list:
                round_scores.append(item[i]['final_score'] if i < len(item) else item[-1]['final_score'])
                round_strict_scores.append(item[i]['strict_final_score'] if i < len(item) else item[-1]['strict_final_score'])
            print(f"Round {i+1} Meeseeks Score: {sum(round_scores)/total}", flush=True)
            print(f"Round {i+1} Utility Rate: {sum(round_strict_scores)/total}", flush=True)
            score_dict[f"round_{i+1}_meeseeks_score"] = sum(round_scores)/total
            score_dict[f"round_{i+1}_ultility_score"] = sum(round_strict_scores)/total
            print("=" * 30)

        # Save Data
        root_dir = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        os.makedirs(root_dir, exist_ok=True)
        # record basic data
        with open(f"{root_dir}/multi_turn_request_list.json", "w") as f:
            json.dump(multi_turn_request_list, f, indent=4, ensure_ascii=False)
        with open(f"{root_dir}/multi_turn_result_list.json", "w") as f:
            json.dump(multi_turn_result_list, f, indent=4, ensure_ascii=False)
        with open(f"{root_dir}/model_score_result_list.json", "w") as f:
            json.dump(model_score_result_list, f, indent=4, ensure_ascii=False)
        with open(f"{root_dir}/extracted_content_list.json", "w") as f:
            json.dump(extracted_content_list, f, indent=4, ensure_ascii=False)
        with open(f"{root_dir}/score.json", "w") as f:
            json.dump(score_dict, f, indent=4, ensure_ascii=False)
        # record round data
        for round in range(self.total_rounds):
            # 缓存每一轮的结果
            result_info = []
            for result in model_score_result_list:
                if round >= len(result):
                    result_info.append(result[-1])  # 读取最后一轮的结果
                else:
                    result_info.append(result[round])  # 读取最后一轮的结果

            detail_capability_result = self.get_capability_result(result_info)
            with open(f"{root_dir}/capability_report_round_{round}.json", "w") as f:
                json.dump(detail_capability_result, f, indent=4, ensure_ascii=False)

    def get_capability_result(self, result_info):
        data = result_info
        capability_list = {}
        total_correct = 0
        total_wrong = 0
        for item in data:
            for subq in item["sub_questions"]:
                if "能力项" in subq:
                    normalized_capabilities = subq["能力项"].replace("～", "~")
                    cur_capabilities = normalized_capabilities.split("、")
                    for capability in cur_capabilities:
                        if capability not in capability_list: capability_list[capability] = [0, 0]
                        if subq["eval_result"] == 1:
                            capability_list[capability][0] += 1
                            total_correct += 1
                        else:
                            capability_list[capability][1] += 1
                            total_wrong += 1

        for key, value in capability_list.items():
            percentage = value[0] / (value[0] + value[1])
            print(f"{key}: {percentage:.2%}", value)

        print("=" * 100)

        def calculate_hierarchical_stats(hierarchy, capability_stats):

            result = {}

            for key, value in hierarchy.items():
                correct = 0
                wrong = 0


                if not value:
                    if key in capability_stats:
                        correct = capability_stats[key][0]
                        wrong = capability_stats[key][1]
                else:
                    sub_results = calculate_hierarchical_stats(value, capability_stats)
                    for sub_stats in sub_results.values():
                        correct += sub_stats[0]
                        wrong += sub_stats[1]

                result[key] = [correct, wrong]

            return result

        hierarchical_stats = calculate_hierarchical_stats(hierarchical_relationship, capability_list)

        # 打印结果
        def print_hierarchical_stats(stats, hierarchy, level=0):
            for key, value in stats.items():
                total = value[0] + value[1]
                if total > 0:
                    percentage = value[0] / total
                    indent = "  " * level
                    print(f"{indent}{key}: {percentage:.2%} (correct: {value[0]}, wrong: {value[1]}, total: {total})")
                if key in hierarchy and isinstance(hierarchy[key], dict):
                    print_hierarchical_stats(
                        calculate_hierarchical_stats(hierarchy[key], capability_list),
                        hierarchy[key],
                        level + 1
                    )

        print_hierarchical_stats(hierarchical_stats, hierarchical_relationship)

        def build_stats_dict(stats, hierarchy, level=0):
            result_dict = {}
            for key, value in stats.items():
                total = value[0] + value[1]
                if total > 0:
                    percentage = value[0] / total
                    result_dict[key] = {
                        "percentage": percentage,
                        "correct": value[0],
                        "wrong": value[1],
                        "total": total
                    }

                    if key in hierarchy and isinstance(hierarchy[key], dict):
                        sub_stats = calculate_hierarchical_stats(hierarchy[key], capability_list)
                        result_dict[key]["children"] = build_stats_dict(sub_stats, hierarchy[key], level + 1)

            return result_dict

        stats_dict = build_stats_dict(hierarchical_stats, hierarchical_relationship)

        return stats_dict


