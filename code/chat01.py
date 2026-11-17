from transformers import AutoModelForCausalLM, AutoTokenizer

tok = AutoTokenizer.from_pretrained(r"model/qwen2.5")
md = AutoModelForCausalLM.from_pretrained(r"model/qwen2.5", torch_dtype="auto", device_map="auto")

def ask(q):
    i = tok(q, return_tensors="pt").to(md.device)
    print(i)
    o = md.generate(**i,max_new_tokens=1024,temperature=0.7)
    print(o)
    return tok.decode(o[0],skip_special_tokens=True)
q="""
写一首诗
"""
print(ask(q))
# while True:
#     q = input("你：")
#     if q.strip() == "exit":
#         break
#     print(ask(q))
