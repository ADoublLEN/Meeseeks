def model_item_count(range, model_response):
    res_len = len(model_response)
    if not range[0] <= res_len <= range[1]:
        return 0, f"❌ Count mismatch, number of items generated: {str(res_len)}"
    return 1, f"✅ Count matches, number of items generated: {str(res_len)}"
