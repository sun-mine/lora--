from transformers import AutoModelForCausalLM, AutoTokenizer

model_path = r"model/qwen2.5" # 例如 D:\models\Qwen2.5-3B-Instruct
model = AutoModelForCausalLM.from_pretrained(
    model_path,
    torch_dtype="auto",
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained(model_path)

messages = []
print("===== Qwen2.5-3B 本地对话，输入exit退出 =====")
while True:
    user_input = input("你：")
    if user_input.strip() == "exit":
        break
    messages.append({"role": "user", "content": user_input})
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)
    generated_ids = model.generate(
        **model_inputs,
        max_new_tokens=1024,
        temperature=0.7
    )
    generated_ids = [
        output_ids[len(input_ids):]
        for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]
    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    print(f"Qwen：{response}\n")
    messages.append({"role": "assistant", "content": response})
hi