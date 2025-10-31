from nlp_feedback import analyze_answer

q = "Tell me about yourself."
a = "I am a software engineer with 5 years experience building web applications. I led a team that improved performance by 30%."

result = analyze_answer(q, a)
print('Result:', result)
assert result['score'] > 5, 'Expected score > 5 for a decent answer'
print('Smoke test passed')
