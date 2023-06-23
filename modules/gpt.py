from gpt4free import you

class GPTModule:
    def __init__(self):
        pass

    def __chat_with_gpt(self, prompt):
        chat = []

        response = you.Completion.create(prompt=prompt, chat=chat)

        return response.text

    def summarize(self, title, summary):
        prompt = f"""
        This is some information from a research paper.

        ---------------------------------------------

        title: {title}
        summary: {summary}

        ---------------------------------------------

        Give me a 3 sentence summary:
        Sentence 1 - A simple summary of the paper. Do not start with "This paper is about..." or "The authors of this paper..."
        Sentence 2 - What is the main result of the paper.Do not start with "This paper is about..." or "The authors of this paper..."
        Sentence 3 - Why it is important to the scientific community, and one example application of the provided knowledge. Do not start with "This paper is about..." or "The authors of this paper..."

        Remove any instances of "paper" and "scientists" in the above summary.
        Combine the sentences into 1 paragraph.

        """

        response = self.__chat_with_gpt(prompt)

        return response
    
    def recommend(self, titles, previous_topics):
        topics_string = ""
        for topic in previous_topics:
            topics_string += f"{topic}, "

        titles_string = ""
        for i, title in enumerate(titles):
            titles_string += f"{i+1}. {title}\n"

        prompt = f"""
        I am a scientist who is interested in {topics_string}.

        I am looking at {len(titles_string)} research papers with the titles:
        {titles_string}

        Please reccomend me 5 papers that I should read next.
        Do not give me the titles of the paper, only the number in the list.
        Give me output in the format:
        num1,num2,num3,num4,num5
        """

        response = self.__chat_with_gpt(prompt)

        return response.split(",")

# Can you please read through it and give me 3 key words that describe the paper.
# They should be very simple and intepretable to someone who knows nothing about science.
# For example, "chemistry" is a good keyword, but "electron-electron cusp" is not

# Only give me the list of keywords in the format:
# keyword1, keyword2, keyword3

# Can you please read through it and give me 5 key words that describe the article.
# Only give me the list of keywords in the format:
# keyword1, keyword2, keyword3, keyword4, keyword5

# Keywords 1 and 2 should contain general information about the field the paper is in.


# Keywords 3, 4, and 5 should contain information about the specific topic of the paper:
# Do not become super specific, try to follow general themes.
# Do not take words directly from the paper, but infer what the overall theme of the paper is.
# The words should be as simple as possible. Most of them should be 1 word, not 2 or more.
# They should be general topics, not specific parts of the article. Do not include general terms like "materials" or "experiments."

# Return list.
