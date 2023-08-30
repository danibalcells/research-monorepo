class Question:

    def __init__(self, question_text=None):
        self.question_text = question_text
        self.answer_text = ''

    def set_answer(self, answer_text):
        self.answer_text = answer_text

    def __str__(self):
        return f'{self.question_text}'
