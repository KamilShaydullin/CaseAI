![image](https://github.com/KamilShaydullin/CaseAI/assets/136807105/4c27b452-f462-47ea-a8e8-ec054d13367c)


CaseAI:
As part of a course on Generative AI technologies at INSEAD, I led a team of students to develop a product that would solve recruitment-related problems for consulting candidates and consulting companies.
CaseAI is a chatbot that helps candidates improve critical case interview skills without a competent case preparation partner. For consulting companies, CaseAI provides an opportunity to help incoming candidates and increase their recruitment funnel.
Check out our pitch video: ___

Customer Journey:
1. The user accesses the chatbot via a proprietary interface.
2. The user initiates case practice by communicating with the chatbot by voice.
3. The chatbot gives a generated case that the candidate solves over 30 minutes. Throughout the 30 minutes, the candidate and the chatbot converse back and forth.
4. At the end of the case, the candidate gives recommendations based on the findings.
5. Finally, the chatbot grades the candidate's performance.

Tech stack:
1. Chatbot user interface - The user's answers are recorded in audio format using the PyAudio library.
2. Python application - The recorded audio file is transcribed using OpenAI's Whisper model and sent to a specific OpenAI agent.
3. OpenAI agent - OpenAI agent analyzes a user's answers, performs calculations (calculator functions) and generates responses.
4. Python application - Generated responses are retrieved by the Python application and sent to the chatbot user interface.
5. Chatbot user interface - The agent's responses are displayed in the user interface and read out by a text-to-speech model.

Next steps to improve the product:
1. Finetuning using an extensive library of high-quality cases.
2. Implementation of Retrieval-Augmented Generation (RAG).
3. Optimization of the user interface to enhance usability.
4. Implementation of an internal calculator function to ensure the agent's calculation accuracy.
5. Establish and implement evaluation and feedback metrics to effectively guide the candidate's preparation.
