ROUND_TEMPLATE = """
In the previous round of conversation, your answer did not meet the user's requirements. Now you need to correct your previous answer.
I will provide you with the [Original Question], [Unmet Requirements from Previous Round], and [Previous Answer]. Please provide your corrected answer based on this information. Note: Only output the answer, do not output any additional information.

[Original Question]:
{question}

[Unmet Requirements from Previous Round]:
{errors}

[Previous Answer]:
{previous_answer}

[Your Corrected Answer]:
"""

def multi_round_template_added(data):
    for item in data:
        question = item["og_question"]
        errors = []
        for subq in item["sub_questions"]:
            if subq["eval_result"] == 0:
                errors.append(f"{subq['question']} was not satisfied. Specific unmet information: {subq['eval_explanation']}")
        previous_answer = item["model_response"]
        template = ROUND_TEMPLATE.format(question=question, errors=errors, previous_answer=previous_answer)
        item["question"] = template
    return data
