import copy
import json
from meeseeks_base_framework import MeeseeksBaseFramework
from source.model.base_model import BaseModel


class MeeseeksMultiTurnFramework(MeeseeksBaseFramework):

    def __init__(self, target_model: BaseModel, extract_model: BaseModel, score_model:BaseModel, data_path):
        super().__init__(target_model, extract_model, score_model)
        self.data = json.load(open(data_path, "r"))


    def run(self):
        for data in self.data:
            multi_turn_requests, multi_turn_results, model_score_result, extra_data = self.run_one(data)

        self.summarization()

    def run_one(self, data):

        conv = []

        multi_turn_results = []
        extra_data = {"extracted_content": []}
        model_score_result = []
        multi_turn_requests = []

        # 执行每一轮对话请求
        for round in range(3):
            if round == 0:
                conv.append({'role':'user', 'content': data['question']})
            # get response
            response_text = self.target_model.generate(conv)
            # record request and result
            multi_turn_requests.append(copy.deepcopy(conv))
            multi_turn_results.append(response_text)

            # update conv
            conv.append({'role':'assistant', 'content': response_text})
            detail_batch_info = copy.deepcopy(data)
            detail_batch_info['model_response'] = response_text

            # extract
            extracted_content = self.extract(detail_batch_info)
            extra_data["extracted_content"].append(extracted_content)


            score_result = self.score([extracted_content])


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

        return multi_turn_requests, multi_turn_results, model_score_result, extra_data

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
    def summarization(self, data):
        pass