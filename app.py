import streamlit as st
import time
import requests
import json
from streamlit_autorefresh import st_autorefresh

# --- Configuration and Data ---

# IMPORTANT: PASTE YOUR GOOGLE APPS SCRIPT URL HERE
# This is the most critical step for the leaderboard to work.
LEADERBOARD_API_URL = "https://script.google.com/macros/s/AKfycbzV53s1lhRqpfoHjyzfUmG89BIYFF-Un2HdyhoOgR3OBG6Yc3qFrKKqzt4iMk0vWI2r/exec"

EXAM_CONFIG = {
    "exam_title": "PRT Full Mock Test (180 Questions)",
    "totalTimeInSeconds": 3 * 60 * 60,  # 3 hours
    "marksPerCorrect": 1,
    "marksPerIncorrect": 0,
    "examId": "PRT_Full_Test_2024_Set_8" # Unique ID for this specific exam
}

# --- ALL 180 QUESTIONS ---
RAW_QUIZ_DATA = [
    {
        "id": 1, "subject": "English", "topic": "Sentence Rearrangement",
        "text": "Rearrange the parts in correct order to make a meaningful sentence.\n(a) his tragic end\n(b) and this leads to\n(c) on what to do\n(d) Hamlet is unable to take a decision",
        "options": ["(1) (a) (b) (c) (d)", "(2) (b) (c) (d) (a)", "(3) (d) (c) (b) (a)", "(4) (b) (d) (a) (c)"],
        "correctAnswer": "(3)", "explanation": "The correct order forms the sentence: 'Hamlet is unable to take a decision (d) on what to do (c) and this leads to (b) his tragic end (a).'"
    },
    {
        "id": 2, "subject": "English", "topic": "Grammar",
        "text": "Change the following sentence from Active Voice to Passive Voice.\nThey will start the journey at midnight.",
        "options": ["(1) The journey at midnight will be started by them.", "(2) At midnight, the journey was started by them.", "(3) The journey will be started by them at midnight.", "(4) The journey at midnight was started by them."],
        "correctAnswer": "(3)", "explanation": "The active sentence is in Future Simple tense ('will start'). The passive form is 'will be + past participle'. The object 'The journey' becomes the subject. Thus, the correct passive sentence is 'The journey will be started by them at midnight.'"
    },
    {
        "id": 3, "subject": "English", "topic": "Grammar",
        "text": "Fill in the blank with the correct preposition.\nI am tired ______ walking endlessly.",
        "options": ["(1) with", "(2) of", "(3) from", "(4) off"],
        "correctAnswer": "(2)", "explanation": "The correct idiomatic expression is 'tired of', which means being bored or annoyed with something or someone."
    },
    {
        "id": 4, "subject": "English", "topic": "Grammar",
        "text": "Choose the correct tense form of the underlined expression from the given options.\nHe <u>shall have finished</u> the assignment before I meet him.",
        "options": ["(1) Future Indefinite", "(2) Future Continuous", "(3) Future Perfect", "(4) Future Perfect Continuous"],
        "correctAnswer": "(3)", "explanation": "The structure 'shall/will have + past participle' (finished) indicates the Future Perfect tense, used for an action that will be completed before another future action."
    },
    {
        "id": 5, "subject": "English", "topic": "Grammar",
        "text": "Change the following sentence from Direct Speech to Indirect Speech.\nThe priest said, 'We are all sinners.'",
        "options": ["(1) The priest said that we are all sinners.", "(2) The priest said that they were all sinners.", "(3) That we were all sinners the priest said.", "(4) The priest said that we have all been sinners."],
        "correctAnswer": "(1)", "explanation": "When a direct speech statement is a universal truth or a general fact ('We are all sinners'), the tense does not change in the indirect speech. 'We' remains 'we' as it includes the speaker and all humanity."
    },
    {
        "id": 6, "subject": "English", "topic": "Grammar",
        "text": "Identify the part which contains an error.\n(1)The little girl / (2)can swim / (3)comfortably /, (4)isn't it ?",
        "options": ["(1)", "(2)", "(3)", "(4)"],
        "correctAnswer": "(4)", "explanation": "The question tag must agree with the subject and the auxiliary verb of the main clause. The subject is 'The little girl' (she) and the auxiliary is 'can'. Therefore, the correct tag should be 'can't she?'."
    },
    {
        "id": 7, "subject": "English", "topic": "Vocabulary",
        "text": "Choose the word nearest in meaning to the given word.\nLIBERAL",
        "options": ["(1) broad-minded", "(2) conservative", "(3) hopeful", "(4) decent"],
        "correctAnswer": "(1)", "explanation": "'Liberal' means willing to respect or accept behaviour or opinions different from one's own; open to new ideas. 'Broad-minded' is the closest synonym."
    },
    {
        "id": 8, "subject": "English", "topic": "Vocabulary",
        "text": "Choose the word opposite in meaning to the given word.\nDEARTH",
        "options": ["(1) extravagance", "(2) richness", "(3) grandeur", "(4) plenty"],
        "correctAnswer": "(4)", "explanation": "'Dearth' means a scarcity or lack of something. The direct opposite is 'plenty', which means a large or sufficient amount or quantity."
    },
    {
        "id": 9, "subject": "English", "topic": "Grammar",
        "text": "Identify the part of speech of the underlined word.\nYou won't have permission to go there <u>unless</u> you have a valid permit for that.",
        "options": ["(1) Preposition", "(2) Conjunction", "(3) Adverb", "(4) Interjection"],
        "correctAnswer": "(2)", "explanation": "'Unless' is a subordinating conjunction that connects two clauses: 'You won't have permission to go there' and 'you have a valid permit for that'."
    },
    {
        "id": 10, "subject": "English", "topic": "Grammar",
        "text": "Identify the underlined clause in the given sentence.\nThey lay down <u>when they had finished their work</u>.",
        "options": ["(1) Noun Clause", "(2) Adjective Clause", "(3) Adverb Clause", "(4) Principal Clause"],
        "correctAnswer": "(3)", "explanation": "The underlined clause 'when they had finished their work' specifies the time when the action of the main clause ('They lay down') occurred. Clauses that modify verbs by indicating time, place, manner, or reason are Adverb Clauses."
    },
    {
        "id": 11, "subject": "Hindi", "topic": "Passage",
        "text": "कबीर के व्यक्तित्व में समन्वय था :",
        "options": ["(1) विपरीत विचारों का", "(2) समान विचारों का", "(3) विरोधी तत्वों का", "(4) विरोधी प्रवृत्तियों का"],
        "correctAnswer": "(3)", "explanation": "गद्यांश के अनुसार, 'कबीर के व्यक्तित्व में विरोधी तत्वों का समन्वय था'।"
    },
    {
        "id": 12, "subject": "Hindi", "topic": "Passage",
        "text": "कबीर के बारे में सही कथन नहीं है :",
        "options": ["(1) कबीर उपदेशक थे।", "(2) कबीर कवि थे।", "(3) कबीर ने अपना धर्म सम्प्रदाय चलाया।", "(4) कबीर समाज सुधारक थे।"],
        "correctAnswer": "(3)", "explanation": "गद्यांश में स्पष्ट रूप से कहा गया है कि 'उन्होंने स्वयं कोई धर्म-सम्प्रदाय नहीं चलाया था'।"
    },
    {
        "id": 13, "subject": "Hindi", "topic": "Passage",
        "text": "कबीरदास ने निम्नलिखित में से क्या नहीं किया :",
        "options": ["(1) समाज सुधार", "(2) गृहस्थ धर्म पालन", "(3) संतचित व्यवहार", "(4) धर्म प्रचार"],
        "correctAnswer": "(4)", "explanation": "कबीर ने समाज सुधार किया, गृहस्थ धर्म का पालन किया और संतों जैसा व्यवहार किया, लेकिन उन्होंने किसी नए धर्म का प्रचार-प्रसार नहीं किया।"
    },
    {
        "id": 14, "subject": "Hindi", "topic": "Grammar",
        "text": "'यह मेरा <u>रास्ता</u> है' वाक्य के रेखांकित शब्द में कारक है :",
        "options": ["(1) कर्ता", "(2) करण", "(3) संबंध", "(4) अधिकरण"],
        "correctAnswer": "(3)", "explanation": "वाक्य में 'मेरा' शब्द 'मैं' (सर्वनाम) और 'रास्ता' (संज्ञा) के बीच संबंध स्थापित कर रहा है। अतः यहाँ संबंध कारक है।"
    },
    {
        "id": 15, "subject": "Hindi", "topic": "Grammar",
        "text": "वचन के आधार पर असंगत शब्द युग्म है :",
        "options": ["(1) विद्यार्थी - विद्यार्थियों", "(2) गुब्बारा - गुब्बारे", "(3) कलम - कलमें", "(4) मेज - मेजें"],
        "correctAnswer": "(1)", "explanation": "'विद्यार्थी' शब्द का बहुवचन 'विद्यार्थी' ही होता है (जैसे - एक विद्यार्थी आया, दस विद्यार्थी आए)। 'विद्यार्थियों' इसका तिर्यक रूप है जो कारक चिन्हों के साथ प्रयोग होता है।"
    },
    {
        "id": 16, "subject": "Hindi", "topic": "Vocabulary",
        "text": "'कपड़ा' शब्द का पर्यायवाची शब्द नहीं है :",
        "options": ["(1) पट", "(2) वसन", "(3) धरित्री", "(4) चीर"],
        "correctAnswer": "(3)", "explanation": "'धरित्री' पृथ्वी का पर्यायवाची है। 'पट', 'वसन', और 'चीर' कपड़े के पर्यायवाची हैं।"
    },
    {
        "id": 17, "subject": "Hindi", "topic": "Vocabulary",
        "text": "निम्नलिखित विलोमार्थी शब्द युग्मों में असंगत है :",
        "options": ["(1) कुटिल - सहज", "(2) ज्योति - तम", "(3) जीवित - मृत", "(4) ताप - शीत"],
        "correctAnswer": "(1)", "explanation": "'कुटिल' का विलोम 'सरल' होता है, न कि 'सहज'। अन्य सभी युग्म सही हैं।"
    },
    {
        "id": 18, "subject": "Hindi", "topic": "Grammar",
        "text": "लिंग के आधार पर असंगत शब्द युग्म है :",
        "options": ["(1) श्रीमान् - श्रीमती", "(2) विद्वान् - विदुषी", "(3) युवा - युवती", "(4) दाता - दात्रि"],
        "correctAnswer": "(4)", "explanation": "'दाता' का सही स्त्रीलिंग रूप 'दात्री' होता है, 'दात्रि' नहीं।"
    },
    {
        "id": 19, "subject": "Hindi", "topic": "मुहावरे/लोकोक्ति",
        "text": "'न तीन में न तेरह में' मुहावरे/लोकोक्ति का सटीक अर्थ है :",
        "options": ["(1) कहीं का न रहना", "(2) बेकार हो जाना", "(3) किसी को पक्षधर न होना", "(4) निष्पक्षता का व्यवहार करना"],
        "correctAnswer": "(1)", "explanation": "इस मुहावरे का अर्थ है किसी भी गिनती में न आना या किसी भी समूह में शामिल न होना, अर्थात् महत्वहीन होना या 'कहीं का न रहना'।"
    },
    {
        "id": 20, "subject": "Hindi", "topic": "Grammar",
        "text": "'<u>जिसको</u> बुलाया था, वह बाज़ार गया है।' - वाक्य के रेखांकित शब्द में सर्वनाम है :",
        "options": ["(1) संबंधवाचक", "(2) निजवाचक", "(3) पुरुषवाचक", "(4) निश्चयवाचक"],
        "correctAnswer": "(1)", "explanation": "'जिसको' और 'वह' सर्वनाम वाक्य के दो भागों को जोड़कर संबंध स्थापित कर रहे हैं, इसलिए यह संबंधवाचक सर्वनाम है।"
    },
    {
        "id": 21, "subject": "GK", "topic": "Awards",
        "text": "Who won the Rashtriya Khel Protsahan Puraskar 2022 under the category 'Encouragement to Sports through Corporate Social Responsibility'?",
        "options": ["(1) India Infrastructure Finance Company Limited", "(2) Kalinga Institute of Industrial Technology", "(3) Coal India", "(4) Odisha Industrial Infrastructure Development Corporation"],
        "correctAnswer": "(2)", "explanation": "Kalinga Institute of Industrial Technology (KIIT) was conferred the Rashtriya Khel Protsahan Puruskar 2022 for 'Encouragement to sports through Corporate Social Responsibility'."
    },
    {
        "id": 22, "subject": "GK", "topic": "Awards",
        "text": "Which feature film was awarded the 'Best Feature Film' in the 68th National Film Awards, 2020?",
        "options": ["(1) Soorarai Pottru", "(2) Sivaranjiniyum Innum Sila Pengallum", "(3) Thinkalazcha Nishchayam", "(4) AK Ayyappanum Koshiyum"],
        "correctAnswer": "(1)", "explanation": "The Tamil film 'Soorarai Pottru', directed by Sudha Kongara, won the award for Best Feature Film at the 68th National Film Awards."
    },
    {
        "id": 23, "subject": "GK", "topic": "Sports Personalities",
        "text": "Consider the following statements regarding the legendary athlete P T Usha and identify the incorrect statement/s.\n(A) She was elected unopposed as the President of Indian Olympic Association.\n(B) She is the first Olympian to head the IOA.\n(C) She is the first woman President of Indian Olympic Association.\n(D) She is a nominated member of the Rajya Sabha.",
        "options": ["(1) Only (A) is incorrect", "(2) Only (B) is incorrect", "(3) Only (C) is incorrect", "(4) All statements are correct"],
        "correctAnswer": "(4)", "explanation": "All the provided statements about P. T. Usha are factually correct as of late 2022/early 2023. This might be a flawed question, but based on facts, none are incorrect."
    },
    {
        "id": 24, "subject": "GK", "topic": "Awards",
        "text": "Which Book/Title was awarded the Bal Sahitya Puraskar 2022 in Bodo Language by the Sahitya Akademi?",
        "options": ["(1) Langwnani Bokha Gotho", "(2) Bongaon Gudiya", "(3) Gosaini Gwjwn Nwjwr", "(4) Solo Bathani Zolonga"],
        "correctAnswer": "(1)", "explanation": "Dewbar Ramchiary won the Bal Sahitya Puraskar 2022 in Bodo language for the short story collection 'Langwnani Bokha Gotho'."
    },
    {
        "id": 25, "subject": "GK", "topic": "World Leaders",
        "text": "Who won the Presidential election in Brazil which was held in October 2022?",
        "options": ["(1) Luiz Inacio Lula da Silva", "(2) Dilma Rousseff", "(3) Gustavo Bebianno", "(4) Jair Bolsonaro"],
        "correctAnswer": "(1)", "explanation": "Luiz Inácio Lula da Silva, often known as Lula, defeated the incumbent Jair Bolsonaro in the Brazilian presidential election held in October 2022."
    },
    {
        "id": 26, "subject": "Science", "topic": "Chemistry",
        "text": "In propounding the 'Newlands' law of Octaves', John Newlands derived the Idea of Octaves from where?",
        "options": ["(1) Ocean", "(2) Music", "(3) Economy", "(4) Thunder"],
        "correctAnswer": "(2)", "explanation": "John Newlands arranged the elements in order of increasing atomic weight and noticed that every eighth element had properties similar to the first, just like the eighth note in a musical scale (an octave). This analogy to music is where the name 'Law of Octaves' comes from."
    },
    {
        "id": 27, "subject": "History", "topic": "French Revolution",
        "text": "The Political Symbol of the \"Winged Woman\" during French Revolution conveyed which of the following?",
        "options": ["(1) Personification of the law", "(2) Enlightenment", "(3) Symbol of eternity", "(4) Colours of France"],
        "correctAnswer": "(1)", "explanation": "During the French Revolution, the 'Winged Woman' was a symbol used for the personification of the law. It represented that law is above all and applies equally to everyone."
    },
    {
        "id": 28, "subject": "Polity", "topic": "Elections",
        "text": "Election in India for the post of the Vice-President is held in accordance with which of the following?",
        "options": ["(1) System of Alternate Voting", "(2) System of Proportional Representation", "(3) First Past the Post system", "(4) Two Round System"],
        "correctAnswer": "(2)", "explanation": "The Vice-President of India is elected by the members of an electoral college consisting of the members of both Houses of Parliament in accordance with the system of proportional representation by means of the single transferable vote."
    },
    {
        "id": 29, "subject": "Geography", "topic": "Demographics",
        "text": "Which of the following Union Territories in India has the highest percentage of population living in households that use improved sanitation facility according to the National Family Health Survey 2019 - 2021 (NFHS-5)?",
        "options": ["(1) Lakshadweep", "(2) Chandigarh", "(3) Puducherry", "(4) Andaman and Nicobar"],
        "correctAnswer": "(1)", "explanation": "According to the NFHS-5 data, Lakshadweep reported the highest percentage (99.8%) of its population living in households with an improved sanitation facility."
    },
    {
        "id": 30, "subject": "EVS", "topic": "Agriculture",
        "text": "Which among the following is a Rabi Crop?",
        "options": ["(1) Mustard", "(2) Maize", "(3) Cotton", "(4) Paddy"],
        "correctAnswer": "(1)", "explanation": "Rabi crops are sown in winter (October-December) and harvested in summer (April-June). Mustard is a major Rabi crop. Maize, Cotton, and Paddy (rice) are Kharif crops."
    },
    {
        "id": 31, "subject": "Reasoning", "topic": "Number Series",
        "text": "How many pairs of consecutive numbers are there in the following number sequence each of which is in ascending order (Like 1, 2)?\n7 6 7 8 6 7 5 6 8 7 7 8 6 5 4 5 6 3 4",
        "options": ["(1) 5", "(2) 6", "(3) 7", "(4) 8"],
        "correctAnswer": "(4)", "explanation": "Let's find the pairs (N, N+1): \n1. (6, 7) \n2. (7, 8) \n3. (6, 7) \n4. (5, 6) \n5. (7, 8) \n6. (4, 5) \n7. (5, 6) \n8. (3, 4) \nThere are 8 such pairs."
    },
    {
        "id": 32, "subject": "Reasoning", "topic": "Seating Arrangement",
        "text": "Eight birds Z, Y, X, W, V, U, T and S are sitting on the corners of octagonal fencing, facing towards the centre. 'Y' is sitting between 'T' and 'W'. 'S' is third to the left of 'Y' and second to the right of 'Z'. 'X' is between 'Z' and 'T'. 'Y' and 'V' are not sitting opposite to each other. Who is second to the left of V?",
        "options": ["(1) S", "(2) U", "(3) X", "(4) Z"],
        "correctAnswer": "(2)", "explanation": "Following the conditions, the final arrangement (clockwise) is: V, X, T, Y, W, S, U, Z. Looking at the arrangement, U is second to the left of V."
    },
    {
        "id": 33, "subject": "Reasoning", "topic": "Direction Sense",
        "text": "A man walks 10 metres towards west and turns to right, walks 8 metres and turns to left, walks 7 metres and turns to right, walks 5 metres. He then turns to right, walks 20 metres and finally turns to right and walks 3 metres. In which direction is he facing now?",
        "options": ["(1) East", "(2) West", "(3) South", "(4) North"],
        "correctAnswer": "(3)", "explanation": "Let's trace the facing direction: Starts West -> Right turn -> North -> Left turn -> West -> Right turn -> North -> Right turn -> East -> Right turn -> South. He is finally facing South."
    },
    {
        "id": 34, "subject": "Reasoning", "topic": "Data Sufficiency",
        "text": "Q : What is the rank of Raju from the top in a class of 30 students?\nStatement I : Raju's rank from the top is two ranks below Jatin who ranks 27th from the bottom.\nStatement II : Raju ranks four ranks above Meenu who ranks 21st from the bottom.",
        "options": ["(1) Data in statement I alone is sufficient", "(2) Data in statement II alone is sufficient", "(3) Data in either statement I or statement II alone are sufficient", "(4) Data in both the statements I and II together are necessary"],
        "correctAnswer": "(3)", "explanation": "From I: Jatin's rank from top = 30 - 27 + 1 = 4th. Raju is 2 ranks below, so Raju is 6th from top. (Sufficient)\nFrom II: Meenu's rank from top = 30 - 21 + 1 = 10th. Raju is 4 ranks above, so Raju is 6th from top. (Sufficient)\nSince both statements alone are sufficient, the answer is 'Either I or II'."
    },
    {
        "id": 35, "subject": "Reasoning", "topic": "Venn Diagram",
        "text": "In the given diagram, how many urban persons are skilled, optimistic and tactful?",
        "options": ["(1) 6", "(2) 9", "(3) 7", "(4) 4"],
        "correctAnswer": "(2)", "explanation": "This question requires a Venn diagram which is not provided in the text. Assuming a standard diagram for this type of question, the answer '9' would represent the intersection of the sets for 'urban', 'skilled', 'optimistic', and 'tactful'."
    },
    {
        "id": 36, "subject": "Computer Science", "topic": "Hardware",
        "text": "Which of the following devices is not used as an output device?",
        "options": ["(1) Printer", "(2) Mouse", "(3) Monitor", "(4) Speaker"],
        "correctAnswer": "(2)", "explanation": "A mouse is an input device used to send signals/commands to the computer. A printer, monitor, and speaker are all output devices that present information from the computer to the user."
    },
    {
        "id": 37, "subject": "Computer Science", "topic": "Software",
        "text": "Which of the following is popular example of web browsers?",
        "options": ["(1) Microsoft Edge", "(2) Microsoft Office", "(3) Microsoft Teams", "(4) Microsoft Outlook"],
        "correctAnswer": "(1)", "explanation": "Microsoft Edge is a web browser used to access the internet. Microsoft Office is a suite of productivity software, Teams is a collaboration platform, and Outlook is an email client."
    },
    {
        "id": 38, "subject": "Computer Science", "topic": "Security",
        "text": "Which of the following is not usually a source of the viruses entering your system?",
        "options": ["(1) Pen drive", "(2) Microphone", "(3) Email attachments", "(4) Downloaded free software"],
        "correctAnswer": "(2)", "explanation": "Viruses are malicious software programs. Pen drives, email attachments, and downloaded software are common vectors for transmitting these programs. A microphone is a hardware device for capturing audio and cannot transmit software viruses."
    },
    {
        "id": 39, "subject": "Computer Science", "topic": "Networks",
        "text": "Which type of computer network is generally configured when two buildings of a school, located within same campus, are connected together using optical fibre to share some data?",
        "options": ["(1) Personal Area Network", "(2) Local Area Network", "(3) Metropolitan Area Network", "(4) Wide Area Network"],
        "correctAnswer": "(2)", "explanation": "A Local Area Network (LAN) is a network that connects computers within a limited geographical area such as a school, office building, or home. Connecting two buildings on the same campus falls under the definition of a LAN."
    },
    {
        "id": 40, "subject": "Computer Science", "topic": "Internet",
        "text": "In the browsing protocol https, 's' stands for?",
        "options": ["(1) Secure", "(2) System", "(3) Services", "(4) Software"],
        "correctAnswer": "(1)", "explanation": "HTTPS stands for Hypertext Transfer Protocol Secure. The 'S' indicates that the communication between your browser and the website is encrypted for security."
    },
    {
        "id": 41, "subject": "Pedagogy", "topic": "Growth & Development",
        "text": "Which one of the following statements is incorrect?",
        "options": [ "(1) Growth is a broader term than development.", "(2) Development is a broader term than growth.", "(3) Growth refers to quantitative changes.", "(4) Development refers to qualitative changes as well." ],
        "correctAnswer": "(1)", "explanation": "Development is a comprehensive and broader term. It includes growth (quantitative changes like increase in height and weight) as well as qualitative changes (like improvements in skills, emotions, and intellect). Therefore, the statement that growth is broader than development is incorrect."
    },
    {
        "id": 42, "subject": "Pedagogy", "topic": "Growth & Development",
        "text": "Which of the following is correct?\nAt the time of birth an infant's head happens to be _________ of his/her total length.",
        "options": ["(1) 1/3", "(2) 1/4", "(3) 1/6", "(4) 1/8"],
        "correctAnswer": "(2)", "explanation": "Due to the principle of cephalocaudal development (head-to-toe), the head develops faster. At birth, an infant's head is disproportionately large, making up about one-fourth of the total body length."
    },
    {
        "id": 43, "subject": "Pedagogy", "topic": "Child Development",
        "text": "Read the following characteristics of a child:\n(a) Child is acquiring simple basic language skills and is able to express himself.\n(b) Has developed 'we' feeling for his playmates and friends.\n(c) Is able to exercise reasonable control over his emotions.\nAt which stage of development the child is?",
        "options": ["(1) Infancy", "(2) Early childhood", "(3) Later childhood", "(4) Adolescence"],
        "correctAnswer": "(3)", "explanation": "These characteristics, particularly the development of a 'we' feeling (peer group importance) and emotional control, are hallmarks of the Later Childhood stage (approximately 6 to 12 years)."
    },
    {
        "id": 44, "subject": "Pedagogy", "topic": "Child Development",
        "text": "Which of the following statements is not a developmental task of adolescence?",
        "options": ["(1) Accepting one's physique and using the body effectively.", "(2) Look forward to marriage and family life.", "(3) Achieving emotional independence of parents and other adults.", "(4) Preparing for an economic career."],
        "correctAnswer": "(2)", "explanation": "While adolescents may think about future relationships, actively preparing for and looking forward to marriage and family life is more characteristic of the developmental tasks of Early Adulthood, as defined by theorists like Havighurst."
    },
    {
        "id": 45, "subject": "Pedagogy", "topic": "Cognitive Development",
        "text": "Which one of the following does not belong to Piaget's 'formal operational stage'?",
        "options": ["(1) Inductive thinking", "(2) Hypothetical - Deductive thinking", "(3) Inter propositional logic", "(4) Combinatorial thinking"],
        "correctAnswer": "(1)", "explanation": "Hypothetical-deductive thinking (reasoning from general principles to specific outcomes), inter-propositional logic (evaluating the logic of statements), and combinatorial thinking (systematically considering all possibilities) are key features of the formal operational stage. Inductive thinking (reasoning from specific observations to general principles) is more characteristic of the concrete operational stage."
    },
    {
        "id": 46, "subject": "Pedagogy", "topic": "Child Development",
        "text": "At which age group children develop recognition of needs and desires of other children?",
        "options": ["(1) From 5 to 8 years", "(2) From 9 to 11 years", "(3) From 12 to 14 years", "(4) After 14 years"],
        "correctAnswer": "(2)", "explanation": "During later childhood (approx. 9-11 years), children's social cognition develops significantly. They move beyond egocentrism and become better at perspective-taking, which allows them to recognize and understand the needs and desires of others."
    },
    {
        "id": 47, "subject": "Pedagogy", "topic": "Character Development",
        "text": "At which stage of character development, internal self criticism occurs?",
        "options": ["(1) Amoral stage", "(2) Self centred stage", "(3) Conforming, conventional stage", "(4) Irrational conscientious stage"],
        "correctAnswer": "(4)", "explanation": "The development of a conscience (superego) leads to internal self-criticism. In the 'irrational conscientious stage', a child internalizes parental rules and feels guilt or self-criticism for breaking them, even if the reasoning behind the guilt is not yet fully rational."
    },
    {
        "id": 48, "subject": "Pedagogy", "topic": "Emotional Development",
        "text": "Complete the sentence:\n'Emotions are caught and not taught'. Therefore, teachers should _________ .",
        "options": ["(1) ask children to control their emotions.", "(2) put their own example before the children for the refined emotional expressions and behaviour.", "(3) make the children familiar with emotional symbols.", "(4) not exhibit their emotions before children."],
        "correctAnswer": "(2)", "explanation": "The phrase 'caught, not taught' implies that children learn emotions through observation and social contagion (modeling). Therefore, the most effective way for a teacher to foster healthy emotional development is to model appropriate emotional expression and behavior themselves."
    },
    {
        "id": 49, "subject": "Pedagogy", "topic": "Socialization",
        "text": "Which one of the following is the most important primary agency for socialization of a child?",
        "options": ["(1) Peers", "(2) Siblings", "(3) Family", "(4) Pre schooling"],
        "correctAnswer": "(3)", "explanation": "The family is universally considered the first and most influential (primary) agent of socialization. It is within the family that a child first learns language, values, norms, and social behaviors."
    },
    {
        "id": 50, "subject": "Pedagogy", "topic": "Growth & Development",
        "text": "Orderly changes that unfold from within are related to:",
        "options": ["(1) Maturation", "(2) Growth", "(3) Development", "(4) Evolution"],
        "correctAnswer": "(1)", "explanation": "Maturation refers to the process of development in which an individual matures or reaches full functionality. These are genetically pre-programmed, orderly changes that unfold naturally over time, relatively independent of the environment (e.g., learning to walk)."
    },
    {
        "id": 51, "subject": "Pedagogy", "topic": "Assessment",
        "text": "Which one of the following statements is correct?",
        "options": [ "(1) Creativity test gives more weightage to novelty and originality.", "(2) Intelligence tests emphasize fluency and flexibility.", "(3) Creativity tests are measures of accuracy.", "(4) Intelligence tests also test creative abilities." ],
        "correctAnswer": "(1)", "explanation": "The defining characteristics of creativity are novelty (uniqueness) and originality. While intelligence tests focus on convergent thinking (finding one correct answer), creativity tests focus on divergent thinking, where novelty and originality are highly valued."
    },
    {
        "id": 52, "subject": "Pedagogy", "topic": "Behavior",
        "text": "Individual behaviour happens to be an outcome of the individual's:",
        "options": ["(1) acquired traits", "(2) biological endowment", "(3) interaction with social and physical environments", "(4) effort for crisis management"],
        "correctAnswer": "(3)", "explanation": "Modern psychology emphasizes that behavior is a product of the continuous and dynamic interaction between a person's hereditary factors (nature) and their social and physical environments (nurture)."
    },
    {
        "id": 53, "subject": "Pedagogy", "topic": "School Role",
        "text": "It will be most desirable, if schools concentrate on:",
        "options": ["(1) preparation for academic excellence.", "(2) development of traits of good citizenship.", "(3) development of traits to face the hurdles of daily life.", "(4) development of modern manners."],
        "correctAnswer": "(3)", "explanation": "While all options are important, the most encompassing and desirable goal is to equip students with the skills, knowledge, resilience, and adaptability to face the various challenges (academic, social, personal) of daily life. This is a holistic view of education."
    },
    {
        "id": 54, "subject": "Pedagogy", "topic": "Socialization",
        "text": "Schools can be called social agents if they:",
        "options": ["(1) organise various activities.", "(2) transmit knowledge.", "(3) educate about rights and duties.", "(4) impart knowledge about traditions and values."],
        "correctAnswer": "(4)", "explanation": "A key function of schools as agents of socialization is to transmit the culture of the society to the next generation. This includes imparting knowledge about societal traditions, norms, and values, helping children integrate into the wider community."
    },
    {
        "id": 55, "subject": "Pedagogy", "topic": "Cognitive Development",
        "text": "Meena is a student who can think hypothetically and deductively, can solve abstract problems and is concerned about personal identity.\nShe is at which stage according to Piaget's stages of Cognitive development?",
        "options": ["(1) Sensory motor", "(2) Pre operational", "(3) Concrete operational", "(4) Formal operational"],
        "correctAnswer": "(4)", "explanation": "The ability to think hypothetically (about 'what if' scenarios), use deductive reasoning, handle abstract concepts, and engage in introspection about identity are the defining characteristics of Piaget's Formal Operational Stage (adolescence and beyond)."
    },
    {
        "id": 56, "subject": "Pedagogy", "topic": "Curriculum Development",
        "text": "Which one of the following is not a key point for curriculum development in child centred approach?",
        "options": ["(1) Selection of content and setting priorities based on teacher's expertise", "(2) Study of students' abilities and backgrounds", "(3) Determining methods and strategies for learning the content", "(4) Determining the procedures of monitoring, assessment and evaluation"],
        "correctAnswer": "(1)", "explanation": "In a child-centered approach, the curriculum is flexible and emerges from the interests, needs, and abilities of the students. Pre-selecting content and setting priorities based solely on the teacher's expertise is characteristic of a teacher-centered or subject-centered approach."
    },
    {
        "id": 57, "subject": "Pedagogy", "topic": "Assessment",
        "text": "Diagnostic assessment is a part of:",
        "options": ["(1) Assessment for learning.", "(2) Assessment of learning.", "(3) Assessment as learning.", "(4) Summative assessment."],
        "correctAnswer": "(1)", "explanation": "Diagnostic assessment is used to identify students' specific strengths and weaknesses before or during instruction. This information is then used to guide teaching and provide targeted support, which is the core purpose of Assessment for Learning (formative assessment)."
    },
    {
        "id": 58, "subject": "Pedagogy", "topic": "Teaching Approaches",
        "text": "For following 'Competency Based Approach' one would not require:",
        "options": ["(1) Preparing the list of competencies to be achieved", "(2) Arranging competencies in order of increasing difficulty", "(3) Identifying prerequisites of learning and making it a part of teaching-learning", "(4) Ensuring course coverage during stipulated time limit"],
        "correctAnswer": "(4)", "explanation": "Competency-Based Education (CBE) is mastery-based, not time-based. The focus is on students demonstrating specific skills and competencies, regardless of how long it takes. Therefore, rigidly ensuring course coverage within a fixed time limit is contrary to the flexible, self-paced philosophy of CBE."
    },
    {
        "id": 59, "subject": "Pedagogy", "topic": "Teaching Approaches",
        "text": "Which one of the following is not a strength of experiential learning?",
        "options": ["(1) It provides immediate feedback for refinement of one's actions.", "(2) It bridges the gap between theory and practice.", "(3) It increases self confidence of students in their work.", "(4) It is less time consuming and cost effective."],
        "correctAnswer": "(4)", "explanation": "Experiential learning, which involves hands-on activities, projects, and real-world experiences, is often more time-consuming and can be more resource-intensive (costly) than traditional classroom instruction. Its strengths lie in its effectiveness, not its efficiency."
    },
    {
        "id": 60, "subject": "Pedagogy", "topic": "Teacher Role",
        "text": "A teacher can establish rapport with students by:",
        "options": ["(1) becoming an authority figure.", "(2) playing a role of a guide.", "(3) implementing rules strictly.", "(4) impressing the students with his knowledge of the subject."],
        "correctAnswer": "(2)", "explanation": "Rapport is built on trust, mutual respect, and support. By acting as a guide who helps and supports students in their learning journey, a teacher fosters a positive and trusting relationship, which is more effective for building rapport than being a strict authority figure."
    },
    {
        "id": 61, "subject": "Pedagogy", "topic": "Teaching Approaches",
        "text": "Which one of the following is the limitation of Constructivist approach?",
        "options": ["(1) It makes learning a passive process.", "(2) It may neglect the importance of foundational knowledge.", "(3) It is not suitable for developing problem solving skills.", "(4) It does not cater to individual differences."],
        "correctAnswer": "(2)", "explanation": "A common criticism of purely constructivist approaches is that in the process of allowing students to construct their own knowledge, they might miss out on essential foundational concepts or develop misconceptions if not guided properly. The unstructured nature can sometimes lead to gaps in core knowledge."
    },
    {
        "id": 62, "subject": "Pedagogy", "topic": "Assessment",
        "text": "Which one of the following is correct?",
        "options": [ "(1) Measurement and evaluation are same.", "(2) Measurement is a broader term than evaluation.", "(3) Evaluation refers to value judgement made on a phenomena based on both qualitative and quantitative information.", "(4) Measurement involves value judgement." ],
        "correctAnswer": "(3)", "explanation": "This statement correctly defines evaluation. Measurement is the quantitative part (assigning a number, e.g., 'scored 80/100'), while evaluation is a broader process that includes measurement but also involves making a value judgment based on that data (e.g., '80/100 is an excellent score')."
    },
    {
        "id": 63, "subject": "Pedagogy", "topic": "Assessment",
        "text": "Which restriction will be of no avail in converting an essay type question into a restricted response item?",
        "options": ["(1) Length of response", "(2) Content of response", "(3) Duration of response", "(4) Format of response"],
        "correctAnswer": "(4)", "explanation": "Restricting the length, content, and time (duration) are all valid ways to make an essay question more focused (a restricted response). However, restricting the 'format' is vague and less meaningful in this context. A student can present the same restricted content in various formats (bullets, paragraphs), so this restriction is of little use."
    },
    {
        "id": 64, "subject": "Pedagogy", "topic": "Learning",
        "text": "Which one of the following is an essential thing to be borne in mind while forming group of students?",
        "options": ["(1) Academic achievement of students", "(2) Intelligence level of students", "(3) Social background of students", "(4) Possibility of equal participation"],
        "correctAnswer": "(4)", "explanation": "For effective collaborative learning, the most crucial factor is ensuring that the group is structured in a way that promotes equal participation from all members. This involves considering group dynamics, assigning roles, and setting clear tasks to prevent a few students from dominating."
    },
    {
        "id": 65, "subject": "Pedagogy", "topic": "Planning",
        "text": "Which of the following information is not contained in the Unit Plan?",
        "options": ["(1) Major and Minor concepts to be developed", "(2) Total number of periods required for transacting the unit", "(3) The method and strategies for transacting the unit", "(4) The specific names of the students who need remedial teaching"],
        "correctAnswer": "(4)", "explanation": "A Unit Plan is a blueprint for teaching a specific unit of content. It outlines objectives, concepts, methods, and assessment strategies. It is created before teaching begins, so it cannot contain the names of specific students who will need remedial help, as this can only be identified after assessment."
    },
    {
        "id": 66, "subject": "Pedagogy", "topic": "Learning",
        "text": "Which one of the following is not a characteristic of learning process?",
        "options": ["(1) Learning is a life long process.", "(2) Learning results in change in behaviour.", "(3) Learning is directly observable.", "(4) Learning is a goal directed process."],
        "correctAnswer": "(3)", "explanation": "Learning is an internal mental process and cannot be directly observed. We can only observe the *outcomes* of learning, which are the changes in a person's behavior or performance. The process itself is cognitive."
    },
    {
        "id": 67, "subject": "Pedagogy", "topic": "Assessment",
        "text": "Which one is not a function of achievement test?",
        "options": ["(1) Informing students about their progress", "(2) Comparing achievement among students regarding acquisition of knowledge", "(3) Modifying the teaching strategies", "(4) Predicting future success of students"],
        "correctAnswer": "(4)", "explanation": "Achievement tests measure what a student has learned or achieved up to a certain point. While they can indicate potential, their primary function is not to predict future success. Tests designed specifically for prediction are called aptitude tests."
    },
    {
        "id": 68, "subject": "Pedagogy", "topic": "Teaching Methods",
        "text": "Which of the following statements is true about multigrade teaching situation?",
        "options": ["(1) There is limited scope for peer tutoring.", "(2) A single teaching learning material is sufficient.", "(3) It promotes dependency of students on teacher.", "(4) Variety of experiences are rich and diverse."],
        "correctAnswer": "(4)", "explanation": "In a multigrade classroom, students of different ages and abilities learn together. This creates a rich and diverse learning environment with numerous opportunities for peer tutoring, collaborative learning, and a wide variety of social and academic experiences."
    },
    {
        "id": 69, "subject": "Pedagogy", "topic": "Assessment",
        "text": "Which of the following statements is not true about peer assessment?",
        "options": ["(1) Peer assessment promotes learning through teaching.", "(2) Peer assessment helps students develop skills in meta-cognition.", "(3) Peer assessment can not be used for summative purposes.", "(4) Peer assessment helps students to be more responsible for learning."],
        "correctAnswer": "(3)", "explanation": "While peer assessment is most commonly used for formative purposes (to improve learning), it can be structured and implemented rigorously to be used for summative purposes (grading), especially when clear rubrics and training are provided. Therefore, the statement that it *cannot* be used for summative purposes is not strictly true."
    },
    {
        "id": 70, "subject": "Pedagogy", "topic": "Questioning",
        "text": "While asking a problem question in a class which of the following can affect the response adversely?",
        "options": ["(1) Giving clues", "(2) Use of double negatives", "(3) Length of the question", "(4) Asking question from the whole class"],
        "correctAnswer": "(2)", "explanation": "Using double negatives (e.g., 'Which of these is not an incorrect answer?') makes a question grammatically complex and confusing. This cognitive load can hinder students' ability to understand what is being asked, thus adversely affecting their response."
    },
    {
        "id": 71, "subject": "Pedagogy", "topic": "Inclusive Education",
        "text": "Normally 'Inclusive Education' in the Indian context is referred to:",
        "options": ["(1) Girls Education", "(2) Divyangjan Education", "(3) Adult Education", "(4) Non-formal Education"],
        "correctAnswer": "(2)", "explanation": "While inclusive education is a broad concept for all learners, in the Indian policy and discourse (e.g., RTE Act, NEP 2020), it most strongly and specifically refers to the inclusion of children with disabilities (Divyangjan) in mainstream schools with appropriate support."
    },
    {
        "id": 72, "subject": "Pedagogy", "topic": "Mental Health",
        "text": "What do you understand by the term 'Mental health' in school education?",
        "options": ["(1) Absence of mental illness", "(2) Capacity of adjustment", "(3) Cognitive, Behavioural and Emotional well being", "(4) Capacity to judge"],
        "correctAnswer": "(3)", "explanation": "Modern definitions of mental health go beyond the mere absence of illness. The World Health Organization (WHO) defines it as a state of well-being, which encompasses cognitive (thinking), behavioral (acting), and emotional well-being."
    },
    {
        "id": 73, "subject": "Pedagogy", "topic": "Mental Health",
        "text": "Which one of the following is most relevant to address 'Mental disorder' in school children?",
        "options": ["(1) Organising debate competition in schools.", "(2) Organising sports competition in schools.", "(3) Promoting group learning in schools.", "(4) Regular appointment of professional counsellors in schools."],
        "correctAnswer": "(4)", "explanation": "Addressing mental disorders requires specialized knowledge and skills. Having trained, professional counselors available in schools is the most direct, appropriate, and effective measure to identify, support, and provide interventions for students facing mental health challenges."
    },
    {
        "id": 74, "subject": "Pedagogy", "topic": "Socialization",
        "text": "The 'Community Centres' in society would ensure:",
        "options": ["(1) Economic well being among children", "(2) Socialisation among children", "(3) Spiritual well being among children", "(4) Emotional well being among children"],
        "correctAnswer": "(2)", "explanation": "A primary function of community centers is to provide a shared space for people, including children, to interact, participate in group activities, and build social connections. This process directly contributes to their socialization."
    },
    {
        "id": 75, "subject": "Pedagogy", "topic": "Special Education",
        "text": "The condition of 'Inability to learn' among school children is normally referred to as:",
        "options": ["(1) Dyslexia", "(2) Dysgraphia", "(3) Autism", "(4) Learning Disability"],
        "correctAnswer": "(4)", "explanation": "'Learning Disability' is the broad, umbrella term for a range of conditions that affect the ability to learn. Dyslexia (reading difficulty) and Dysgraphia (writing difficulty) are specific types of learning disabilities."
    },
    {
        "id": 76, "subject": "GK", "topic": "Government Policies",
        "text": "What is the minimum quantum of disability prescribed to avail benefits for Divyangjan children under the RPwD Act, 2016?",
        "options": ["(1) 25%", "(2) 50%", "(3) 40%", "(4) 35%"],
        "correctAnswer": "(3)", "explanation": "The Rights of Persons with Disabilities (RPwD) Act, 2016 in India defines a 'person with benchmark disability' as someone having not less than 40 percent of a specified disability. This is the threshold for availing various government benefits and reservations."
    },
    {
        "id": 77, "subject": "Pedagogy", "topic": "Special Education",
        "text": "The 'Small sized head' among school children is technically known as __________ in medical science.",
        "options": ["(1) Dwarfism", "(2) Microcephaly", "(3) Megacephaly", "(4) Cretinism"],
        "correctAnswer": "(2)", "explanation": "Microcephaly is the medical term for a condition where a baby's head is significantly smaller than expected. Megacephaly is the opposite (large head). Dwarfism refers to short stature, and Cretinism is a condition of severely stunted physical and mental growth due to untreated congenital thyroid deficiency."
    },
    {
        "id": 78, "subject": "GK", "topic": "Government Policies",
        "text": "The programme 'Manodarpan' recently launched by Ministry of Education, Govt. of India, refers to:",
        "options": ["(1) Social development of children", "(2) Physical development of children", "(3) Mental health of children", "(4) Emotional development of children"],
        "correctAnswer": "(3)", "explanation": "The 'Manodarpan' initiative was launched by the Ministry of Education to provide psychosocial support and counseling to students, teachers, and families for their mental health and emotional well-being during the COVID-19 pandemic and beyond."
    },
    {
        "id": 79, "subject": "Pedagogy", "topic": "School Counseling",
        "text": "Which one of the following is essential for professional health counsellors in schools?",
        "options": ["(1) Empathy", "(2) Emotions", "(3) Sympathy", "(4) Apathy"],
        "correctAnswer": "(1)", "explanation": "Empathy, the ability to understand and share the feelings of another, is the most crucial quality for a counselor. It allows them to connect with students on a deeper level. Sympathy is feeling sorry for someone, which is different and can create a power imbalance. Apathy is a lack of feeling."
    },
    {
        "id": 80, "subject": "Pedagogy", "topic": "Mental Health",
        "text": "Which one of the following factors is most accountable for Mental disorder in school children?",
        "options": ["(1) Accidents", "(2) Family atmosphere", "(3) Hormonal imbalances", "(4) Traditions and customs"],
        "correctAnswer": "(2)", "explanation": "While all factors can play a role, the family atmosphere (including factors like conflict, abuse, neglect, or lack of support) is a significant and consistent environmental factor that strongly influences a child's mental and emotional well-being and can contribute to mental health disorders."
    },
    {
        "id": 81, "subject": "Pedagogy", "topic": "Teacher Role",
        "text": "In what sense is a teacher termed as an initiator?",
        "options": ["(1) Teacher gives new ideas.", "(2) Teacher provides all material for learning.", "(3) Teacher voluntarily comes ahead to train students into learning skills.", "(4) Teacher begins the talk in a group."],
        "correctAnswer": "(3)", "explanation": "A teacher is an initiator because they take the proactive step of starting and guiding the learning process. They initiate activities, introduce concepts, and actively train students to develop new skills and knowledge."
    },
    {
        "id": 82, "subject": "Pedagogy", "topic": "Classroom Management",
        "text": "Which one is not a part of team building process?",
        "options": ["(1) Task achievement", "(2) Building and maintenance of the team", "(3) Development of the individuals", "(4) Cognitive process analysis"],
        "correctAnswer": "(4)", "explanation": "Team building involves stages like forming, storming, norming, and performing, which focus on achieving the task, maintaining the team, and developing individuals within the team. Cognitive process analysis is a psychological term related to understanding individual thought processes and is not a standard part of the team building model."
    },
    {
        "id": 83, "subject": "Pedagogy", "topic": "Leadership",
        "text": "Which one of the following is not a part of leadership process?",
        "options": ["(1) Establishing direction", "(2) Assessing cultural background of students", "(3) Motivating people", "(4) Aligning people"],
        "correctAnswer": "(2)", "explanation": "Core leadership processes involve establishing a vision/direction, aligning people with that direction, and motivating them to action. While assessing the cultural background of students is an important and contextually aware practice for a *teacher*, it is not considered a fundamental process of leadership itself."
    },
    {
        "id": 84, "subject": "Pedagogy", "topic": "Teacher Role",
        "text": "Which one of the following is not a part of instructional role of a teacher?",
        "options": ["(1) Evaluating student's progress", "(2) Diagnosis of learning difficulties of students", "(3) Guiding students", "(4) Curriculum Planning"],
        "correctAnswer": "(4)", "explanation": "The instructional role of a teacher involves the direct process of teaching and learning in the classroom, such as evaluating, diagnosing, and guiding students. Curriculum planning, while vital, is a broader, pre-instructional activity that happens before the direct instruction begins."
    },
    {
        "id": 85, "subject": "Pedagogy", "topic": "Teacher Development",
        "text": "Which one of the following helps maximum in developing a sense of empathy among teachers?",
        "options": ["(1) Talking to parents of weak students", "(2) Visits to orphanages", "(3) Giving them more responsibilities", "(4) Appreciating their work frequently"],
        "correctAnswer": "(2)", "explanation": "Empathy is the ability to understand and share the feelings of another. Visiting an orphanage and directly observing the lives and situations of underprivileged children provides a powerful, real-world experience that can deeply foster empathy and perspective-taking in teachers."
    },
    {
        "id": 86, "subject": "Pedagogy", "topic": "Teacher Development",
        "text": "For enhancing one's horizon, which one forum will you recommend to a teacher?",
        "options": ["(1) Students Association", "(2) Teachers Association", "(3) Parents Association", "(4) Old boys Association"],
        "correctAnswer": "(2)", "explanation": "A Teachers' Association is a professional organization specifically designed for teachers to network, share best practices, engage in professional development, and discuss educational issues, thereby enhancing their professional horizons."
    },
    {
        "id": 87, "subject": "Pedagogy", "topic": "School Management",
        "text": "Which school time table period will you suggest for games and sports?",
        "options": ["(1) Last period of the day", "(2) Period just after the recess", "(3) First period in the morning", "(4) Any period as convenient to the teacher"],
        "correctAnswer": "(2)", "explanation": "Placing games and sports just after the recess (lunch break) is often considered ideal. Students have refueled their energy with food and can engage in physical activity without being tired from a full day of classes or too sluggish before the day has begun."
    },
    {
        "id": 88, "subject": "Pedagogy", "topic": "School Leadership",
        "text": "Who can help school principal, Mr.Ali, the most in setting goals for his school?",
        "options": ["(1) His senior secondary students", "(2) A forum of school principals", "(3) A senior teacher of his school", "(4) A parent representative"],
        "correctAnswer": "(2)", "explanation": "A forum of his peers—other school principals—can provide the most valuable help. They share similar experiences, understand the challenges and responsibilities of the role, and can offer practical, tested advice and collaborative support for setting realistic and effective school goals."
    },
    {
        "id": 89, "subject": "Pedagogy", "topic": "Planning",
        "text": "Who can best help the teacher Mr. Sharma in developing his class plan?",
        "options": ["(1) Best and weakest students of his class", "(2) Principal of his school", "(3) Subject expert of his school", "(4) Vice principal of his school"],
        "correctAnswer": "(1)", "explanation": "To create a truly effective and differentiated class plan, a teacher needs to understand the range of learning needs in the classroom. Direct feedback or diagnostic assessment of the highest-achieving ('best') and lowest-achieving ('weakest') students provides the clearest picture of this range, enabling the teacher to plan for all learners."
    },
    {
        "id": 90, "subject": "Pedagogy", "topic": "Community",
        "text": "Which one of the following is a learning community?",
        "options": ["(1) Political Party", "(2) Crowd in a market", "(3) Hobby clubs", "(4) A group of people watching movie in a hall"],
        "correctAnswer": "(3)", "explanation": "A learning community is a group of people who share common values and beliefs, are actively engaged in learning together from each other. A hobby club (e.g., a book club, a coding club) perfectly fits this description as members come together to share, learn, and improve in a specific area of interest."
    },
    {
        "id": 91, "subject": "Pedagogy", "topic": "Aims of Education",
        "text": "What is the major aim of imparting school education according to you?",
        "options": ["(1) Socialization of children", "(2) Information giving to children", "(3) Making children disciplined", "(4) Helping children to earn their livelihood"],
        "correctAnswer": "(1)", "explanation": "While all options are aspects of education, socialization is the most encompassing aim. It refers to the process of preparing individuals to become functioning members of society by instilling skills, knowledge, norms, and values. This broad aim includes aspects of information, discipline, and career preparation."
    },
    {
        "id": 92, "subject": "Education Policy", "topic": "Curriculum Framework",
        "text": "Who emphasized on the integration of essential subjects, skills and capacities?",
        "options": ["(1) NEP - 1986", "(2) POA - 1992", "(3) NCF - 2005", "(4) NPE - 1968"],
        "correctAnswer": "(3)", "explanation": "The National Curriculum Framework (NCF) 2005 strongly advocated for moving away from rote learning and subject-wise silos. It emphasized an integrated approach to knowledge, connecting different subjects and linking learning to life outside the school."
    },
    {
        "id": 93, "subject": "Education Policy", "topic": "Curriculum Framework",
        "text": "Who is expected to design a National Curricular and Pedagogical Framework for Early Childhood Care and Education (NCPFECCE) as per NEP 2020?",
        "options": ["(1) SCERTs", "(2) NCERT", "(3) CIET", "(4) RCI"],
        "correctAnswer": "(2)", "explanation": "The National Education Policy (NEP) 2020 mandates the National Council of Educational Research and Training (NCERT) to develop the National Curricular and Pedagogical Framework for Early Childhood Care and Education (NCPFECCE) for children up to the age of 8."
    },
    {
        "id": 94, "subject": "Pedagogy", "topic": "Teaching Approaches",
        "text": "What is the logic behind advocating competency based learning and education?",
        "options": ["(1) Each teacher has its own way of teaching", "(2) Each school has its own curriculum", "(3) Each state has its own education policy", "(4) Each child learns at its own pace"],
        "correctAnswer": "(4)", "explanation": "The core principle of Competency-Based Learning (CBL) is that learning should be based on mastery, not time. It recognizes that different children learn at different rates. CBL allows students to progress once they have demonstrated mastery of a competency, accommodating their individual learning pace."
    },
    {
        "id": 95, "subject": "Pedagogy", "topic": "School Environment",
        "text": "How a school can make its environment safe and secure for children?",
        "options": ["(1) By punishing the notorious children", "(2) By keeping a strict watch on each and every child", "(3) By maintaining discipline through fear", "(4) By adopting affectionate teaching learning techniques"],
        "correctAnswer": "(4)", "explanation": "A truly safe and secure environment is not just about physical safety but also emotional and psychological safety. Adopting affectionate, supportive, and respectful teaching techniques creates a positive classroom climate where students feel valued and safe to express themselves, which is foundational to overall security."
    },
    {
        "id": 96, "subject": "Pedagogy", "topic": "Child Rights",
        "text": "In the existing educational set up at school level, which right of the children is not properly handled by our teachers?",
        "options": ["(1) Right to express their views", "(2) Right to remain silent", "(3) Right to ask questions", "(4) Right to differ on some points"],
        "correctAnswer": "(1)", "explanation": "While progress has been made, traditional classrooms often prioritize teacher-led instruction, which can limit opportunities for children to fully express their own views, ideas, and opinions. Fostering an environment where children feel safe and encouraged to express themselves remains a challenge."
    },
    {
        "id": 97, "subject": "Education Policy", "topic": "Language in Education",
        "text": "In case of non-availability of mother tongue language teacher, preferably in which language, a primary class student should be taught as per NEP 2020?",
        "options": ["(1) Language of the State", "(2) Hindi", "(3) English", "(4) Regional Language."],
        "correctAnswer": "(4)", "explanation": "NEP 2020 states that the medium of instruction until at least Grade 5, but preferably till Grade 8 and beyond, will be the home language/mother tongue/local language/regional language. This ensures that the child understands concepts better in a familiar language."
    },
    {
        "id": 98, "subject": "Education Policy", "topic": "Education Commissions",
        "text": "Who, among the following invited experts from Russia and America for developing its report?",
        "options": ["(1) Mudaliar Commission - 1952-53", "(2) Radhakrishnan Commission - 1948-49", "(3) Kothari Commission - 1964-66", "(4) Acharya Ram Murthy Commission - 1990"],
        "correctAnswer": "(3)", "explanation": "The Kothari Commission (1964-66), officially known as the Education Commission, was known for its comprehensive and forward-looking approach. It consulted with a panel of 20 international experts from countries like the USA, UK, USSR (Russia), France, and Japan to gain a global perspective on education."
    },
    {
        "id": 99, "subject": "Pedagogy", "topic": "Curriculum",
        "text": "Which one of the following types of curriculum you will recommend for teaching primary classes?",
        "options": ["(1) Integrated Curriculum", "(2) Subject based Curriculum", "(3) Teacher centred Curriculum", "(4) Activity based Curriculum"],
        "correctAnswer": "(1)", "explanation": "An Integrated Curriculum is highly recommended for primary classes. It connects different subject areas (like language, math, and EVS) around a common theme, making learning more meaningful, holistic, and relevant to young children's experiences, rather than fragmenting knowledge into separate subjects."
    },
    {
        "id": 100, "subject": "Pedagogy", "topic": "Teacher Role",
        "text": "For teaching at which of the following level, subject knowledge of the teacher is not as important as other qualities?",
        "options": ["(1) Middle stage", "(2) Secondary stage", "(3) Preparatory stage", "(4) Foundational stage"],
        "correctAnswer": "(4)", "explanation": "At the Foundational Stage (ages 3-8), while basic knowledge is necessary, pedagogical skills related to play-based learning, care, nurturing, patience, and creating a safe and stimulating environment are far more critical than deep subject matter expertise."
    },
    {
        "id": 101, "subject": "Hindi", "topic": "Passage",
        "text": "भारतीय साहित्य की सबसे बड़ी विशेषता क्या है और निम्नलिखित में से किसके बीच समन्वय प्रसिद्ध है?",
        "options": ["(1) ज्ञान, कर्म और भक्ति", "(2) ज्ञान और भक्ति", "(3) कर्म, भक्ति और ज्ञान", "(4) ज्ञान, कर्म और संगीत"],
        "correctAnswer": "(1)", "explanation": "गद्यांश के अनुसार, भारतीय साहित्य की सबसे बड़ी विशेषता 'समन्वय की भावना' है, जिसमें ज्ञान, भक्ति, तथा कर्म का समन्वय प्रसिद्ध है।"
    },
    {
        "id": 102, "subject": "Hindi", "topic": "Passage",
        "text": "निम्नलिखित में गद्यांश के संदर्भ में असंगत शब्द है :",
        "options": ["(1) अज्ञानता", "(2) विक्षिप्तता", "(3) मौलिकता", "(4) सार्थकता"],
        "correctAnswer": "(2)", "explanation": "गद्यांश में 'मौलिकता' और 'सार्थकता' की बात की गई है और 'अज्ञानता' का विपरीत भाव निहित है। 'विक्षिप्तता' (पागलपन) शब्द का संदर्भ गद्यांश के भाव से मेल नहीं खाता।"
    },
    {
        "id": 103, "subject": "Hindi", "topic": "Passage",
        "text": "अपनी किस विशेषता के बल पर भारतीय साहित्य अपनी पताका फहरा सकता है?",
        "options": ["(1) मौलिकता", "(2) लौकिकता", "(3) समन्वय की भावना", "(4) अनेकता"],
        "correctAnswer": "(3)", "explanation": "गद्यांश में स्पष्ट लिखा है कि भारतीय साहित्य की सबसे बड़ी विशेषता 'समन्वय की भावना' है, और इसी के बल पर वह अपनी मौलिकता दिखा सकता है।"
    },
    {
        "id": 104, "subject": "Hindi", "topic": "Passage",
        "text": "निम्नलिखित में कौन-सा युग्म अलौकिक आनंद में विलीन हो जाने पर भी साहित्यिक समन्वय को नहीं दर्शाता?",
        "options": ["(1) हानि - लाभ", "(2) हर्ष - विषाद", "(3) उत्थान - पतन", "(4) सुख - दुःख"],
        "correctAnswer": "(1)", "explanation": "गद्यांश में सुख-दुःख, हर्ष-विषाद, उत्थान-पतन जैसे विरोधी भावों के समन्वय का उल्लेख है। 'हानि-लाभ' का उल्लेख नहीं है और यह व्यावसायिक संदर्भ में अधिक प्रयुक्त होता है।"
    },
    {
        "id": 105, "subject": "Hindi", "topic": "Passage",
        "text": "साहित्यिक समन्वय से अभिप्राय है :",
        "options": ["(1) साहित्य में विरोधी तत्वों का न होना", "(2) साहित्य में केवल समान भावों का होना", "(3) विरोधी और विपरीत भावों का अलौकिक आनंद में विलीन हो जाना", "(4) साहित्य में भावों का अभाव"],
        "correctAnswer": "(3)", "explanation": "गद्यांश के अनुसार, साहित्यिक समन्वय का अर्थ है जब सुख-दुःख, हर्ष-विषाद जैसे विरोधी और विपरीत भाव आपस में इस तरह मिल जाएँ कि वे अलौकिक आनंद में विलीन हो जाएँ।"
    },
    {
        "id": 106, "subject": "Hindi", "topic": "Vocabulary",
        "text": "'भौंरा ' शब्द का कौन-सा पर्यायवाची शब्द है?",
        "options": ["(1) भंजन", "(2) कृति", "(3) भृंग", "(4) विहंगम"],
        "correctAnswer": "(3)", "explanation": "'भृंग', 'मधुप', 'अलि', 'षट्पद' आदि भौंरा के पर्यायवाची शब्द हैं। 'विहंगम' पक्षी का पर्यायवाची है।"
    },
    {
        "id": 107, "subject": "Hindi", "topic": "Grammar",
        "text": "'हस्तलिखित' शब्द उदाहरण है।",
        "options": ["(1) कर्मधारय समास का", "(2) तत्पुरुष समास का", "(3) द्विगु समास का", "(4) बहुव्रीहि समास का"],
        "correctAnswer": "(2)", "explanation": "'हस्तलिखित' का समास विग्रह है 'हस्त से लिखित' (हाथ से लिखा हुआ)। यहाँ 'से' करण कारक की विभक्ति है, अतः यह करण तत्पुरुष समास है।"
    },
    {
        "id": 108, "subject": "Hindi", "topic": "Grammar",
        "text": "तत्सम तद्भव का असंगत युग्म है।",
        "options": ["(1) स्वर्ण - सोना", "(2) जिह्वा - जीभ", "(3) कोकिल - कोयल", "(4) क्षार - खार"],
        "correctAnswer": "(3)", "explanation": "तत्सम शब्द 'कोकिल' का तद्भव रूप 'कोयल' होता है। दिए गए विकल्प में यह उल्टा लिखा है। अन्य सभी युग्म सही हैं।"
    },
    {
        "id": 109, "subject": "Hindi", "topic": "Vocabulary",
        "text": "निम्नलिखित विलोमार्थी शब्द-युग्मों में असंगत है :",
        "options": ["(1) वंश - विवंश", "(2) परतंत्र - स्वतंत्र", "(3) निंदा - स्तुति", "(4) पाप - पुण्य"],
        "correctAnswer": "(1)", "explanation": "'वंश' (lineage) और 'विवंश' (helpless) विलोम शब्द नहीं हैं। इनके अर्थ बिल्कुल अलग हैं। अन्य सभी युग्म सही विलोमार्थी हैं।"
    },
    {
        "id": 110, "subject": "Hindi", "topic": "Grammar",
        "text": "निम्नलिखित में गुणवाचक विशेषण नहीं है :",
        "options": ["(1) बुरा", "(2) तीसरा", "(3) मैला", "(4) लाल"],
        "correctAnswer": "(2)", "explanation": "'बुरा', 'मैला', और 'लाल' गुण या विशेषता बताते हैं, इसलिए ये गुणवाचक विशेषण हैं। 'तीसरा' क्रम का बोध कराता है, इसलिए यह संख्यावाचक विशेषण है।"
    },
    {
        "id": 111, "subject": "Hindi", "topic": "Grammar",
        "text": "निम्नलिखित में से किस शब्द में व्यंजन संधि नहीं है?",
        "options": ["(1) विस्मरण", "(2) अनुसरण", "(3) जगन्नाथ", "(4) नाविक"],
        "correctAnswer": "(4)", "explanation": "'नाविक' का संधि-विच्छेद 'नौ + इक' है, जो अयादि स्वर संधि का उदाहरण है। 'विस्मरण' (वि + स्मरण), 'अनुसरण' (अनु + सरण) में संयोग है और 'जगन्नाथ' (जगत् + नाथ) व्यंजन संधि है।"
    },
    {
        "id": 112, "subject": "Hindi", "topic": "मुहावरे/लोकोक्ति",
        "text": "'सीधी उँगली से घी नहीं निकलता' मुहावरे/लोकोक्ति का सटीक अर्थ है :",
        "options": ["(1) बहुत सीधा होने से काम नहीं चलता", "(2) अच्छे कार्यफल के लिए मेहनत करनी पड़ती है", "(3) बुरे से बुरा व्यवहार करना पड़ता है", "(4) आसानी से काम करना चाहिए"],
        "correctAnswer": "(1)", "explanation": "इस लोकोक्ति का अर्थ है कि हर काम शराफत या सीधेपन से नहीं होता; कभी-कभी अपना काम निकालने के लिए चतुराई या सख्ती दिखानी पड़ती है।"
    },
    {
        "id": 113, "subject": "Hindi", "topic": "Literature",
        "text": "'जहाँ चाह वहाँ राह' रचना किस विधा की है?",
        "options": ["(1) कहानी", "(2) कविता", "(3) लेख", "(4) संस्मरण"],
        "correctAnswer": "(3)", "explanation": "यह रचना (NCERT पाठ्यपुस्तक 'रिमझिम' में) एक लेख या प्रेरक प्रसंग है जो इला सचानी के जीवन पर आधारित है।"
    },
    {
        "id": 114, "subject": "Hindi", "topic": "Literature",
        "text": "'राख की रस्सी' लोक कथा में लोनपोगार ने शहर जा रहे अपने बेटे को क्या दिया?",
        "options": ["(1) बकरियाँ", "(2) भेड़ें", "(3) गाएँ", "(4) घोड़े"],
        "correctAnswer": "(2)", "explanation": "तिब्बत की लोककथा 'राख की रस्सी' में मंत्री लोनपोगार ने अपने बेटे को सौ भेड़ें देकर शहर भेजा था।"
    },
    {
        "id": 115, "subject": "Hindi", "topic": "Literature",
        "text": "'कोई ला के मुझे दे' कविता के रचयिता हैं :",
        "options": ["(1) दामोदर अग्रवाल", "(2) सोहनलाल द्विवेदी", "(3) कल्पना सिंह", "(4) हरिकृष्ण दास गुप्त"],
        "correctAnswer": "(1)", "explanation": "'कोई ला के मुझे दे' कविता (NCERT पाठ्यपुस्तक 'रिमझिम' में) के रचयिता दामोदर अग्रवाल हैं।"
    },
    {
        "id": 116, "subject": "Hindi", "topic": "Literature",
        "text": "\"किसने बटन हमारे कुतरे ? किसने स्याही को बिखराया ?...\" प्रस्तुत काव्यांश किस रचनाकार का है?",
        "options": ["(1) रामधारी सिंह दिनकर", "(2) सोहनलाल द्विवेदी", "(3) कल्पना सिंह", "(4) दामोदर अग्रवाल"],
        "correctAnswer": "(2)", "explanation": "यह पंक्तियाँ सोहनलाल द्विवेदी की कविता 'कौन' से हैं, जो NCERT की पाठ्यपुस्तक 'रिमझिम' में शामिल है।"
    },
    {
        "id": 117, "subject": "Hindi", "topic": "Literature",
        "text": "'बहादुर बित्तो' रचना में बैल की जान कैसे बच गयी?",
        "options": ["(1) बित्तो की हिम्मत और सूझबूझ से", "(2) किसान की चालाकी से", "(3) किसान की बहादुरी से", "(4) गाँव वालों के सहयोग से"],
        "correctAnswer": "(1)", "explanation": "पंजाबी लोककथा 'बहादुर बित्तो' में बित्तो ने अपनी हिम्मत और सूझबूझ से शेर को डराकर भगा दिया, जिससे उसके बैल की जान बच गई।"
    },
    {
        "id": 118, "subject": "Hindi", "topic": "Literature",
        "text": "'चाँद वाली अम्मा' के आधार पर बताइए कि बूढ़ी अम्मा चाँद पर क्यों चढ़ गयी?",
        "options": ["(1) उसकी सुंदरता देखकर", "(2) आसमान से अपना पीछा छुड़ाने के लिए", "(3) चाँद के कहने पर", "(4) चाँद को डराने के लिए"],
        "correctAnswer": "(2)", "explanation": "कहानी 'चाँद वाली अम्मा' में, जब आसमान अम्मा को झाड़ू सहित ऊपर ले जाने लगा, तो अम्मा ने अपना पीछा छुड़ाने के लिए पास में दिखे चाँद पर पैर रख दिया और वहीं बैठ गईं।"
    },
    {
        "id": 119, "subject": "Hindi", "topic": "General Knowledge",
        "text": "निम्नलिखित को सुमेलित कीजिए :\n(A) जलेबी (i) पकौड़ी\n(B) करेला (ii) ठंडा\n(C) कुल्फी (iii) कड़वा\n(D) आलू (iv) मीठी",
        "options": ["(1) (A)-(iv), (B)-(iii), (C)-(ii), (D)-(i)", "(2) (A)-(iii), (B)-(ii), (C)-(i), (D)-(iv)", "(3) (A)-(ii), (B)-(i), (C)-(iv), (D)-(iii)", "(4) (A)-(i), (B)-(iv), (C)-(iii), (D)-(ii)"],
        "correctAnswer": "(1)", "explanation": "सही मिलान है: जलेबी मीठी होती है (A-iv), करेला कड़वा होता है (B-iii), कुल्फी ठंडी होती है (C-ii), और आलू से पकौड़ी बनती है (D-i)।"
    },
    {
        "id": 120, "subject": "Hindi", "topic": "Literature",
        "text": "'अधिक बलवान कौन' रचना के आधार पर बताइए कि आदमी की टोपी कैसे उड़ गयी?",
        "options": ["(1) गर्मी से", "(2) तूफान से", "(3) हवा की ताकत से", "(4) आदमी के दौड़ने से"],
        "correctAnswer": "(3)", "explanation": "कहानी 'अधिक बलवान कौन' में हवा और सूरज के बीच बहस होती है। अपनी ताकत दिखाने के लिए हवा इतनी जोर से चलती है कि आदमी की टोपी उड़ जाती है।"
    },
    {
        "id": 121, "subject": "English", "topic": "Reading Comprehension",
        "text": "Based on the passage, what is a 'dotara'?",
        "options": ["(1) A kitchen utensil", "(2) A household item", "(3) A musical instrument", "(4) A piece of hosiery"],
        "correctAnswer": "(3)", "explanation": "The passage describes the dotara as a 'traditional two-stringed instrument' and mentions the old man used to play it, clearly identifying it as a musical instrument."
    },
    {
        "id": 122, "subject": "English", "topic": "Reading Comprehension",
        "text": "The sight of a dotara changed the old man's expression. How?",
        "options": ["(1) It made him sad and crestfallen.", "(2) It made him proud and happy.", "(3) It filled him with anger.", "(4) It had no effect on him."],
        "correctAnswer": "(2)", "explanation": "The passage states, 'A beatific smile spread on his wrinkled face' and he 'spoke proudly,' indicating that seeing the dotara made him happy and proud."
    },
    {
        "id": 123, "subject": "English", "topic": "Reading Comprehension",
        "text": "What was the old man's response upon seeing the dotara?",
        "options": ["(1) He started talking proudly about his past fame.", "(2) He ignored the new development", "(3) He reacted with shock and anger", "(4) He shouted at his wife"],
        "correctAnswer": "(1)", "explanation": "His immediate response was to smile and proudly talk about his past, saying, 'In my younger days...I was a famous dotara player.'"
    },
    {
        "id": 124, "subject": "English", "topic": "Reading Comprehension",
        "text": "How did the old woman react?",
        "options": ["(1) She admonished her husband for his obsession with the past.", "(2) She did not react to the situation at all.", "(3) She joined her husband in talking about the past", "(4) She kept mum and just looked around"],
        "correctAnswer": "(1)", "explanation": "The passage says she reacted 'peevishly' and said, 'Always bragging about your past! Why don't you talk about our miserable present?' This shows she admonished (scolded) him."
    },
    {
        "id": 125, "subject": "English", "topic": "Reading Comprehension",
        "text": "What does 'peevish' mean?",
        "options": ["(1) Tragic", "(2) Bad-tempered", "(3) Excited", "(4) Foul-smelling"],
        "correctAnswer": "(2)", "explanation": "'Peevish' means easily irritated, especially by unimportant things. 'Bad-tempered' is the closest synonym."
    },
    {
        "id": 126, "subject": "English", "topic": "Sentence Rearrangement",
        "text": "Rearrange the parts in correct order to make a meaningful sentence.\n(a) has adapted\n(b) noted film-maker Vishal Bhardwaj\n(c) for Hindi Cinema\n(d) some of Shakespeare's plays",
        "options": ["(1) (c) (b) (a) (d)", "(2) (b) (c) (d) (a)", "(3) (a) (c) (b) (d)", "(4) (b) (a) (d) (c)"],
        "correctAnswer": "(4)", "explanation": "The correct order is: (b) noted film-maker Vishal Bhardwaj (subject) (a) has adapted (verb) (d) some of Shakespeare's plays (object) (c) for Hindi Cinema (prepositional phrase)."
    },
    {
        "id": 127, "subject": "English", "topic": "Sentence Rearrangement",
        "text": "Rearrange the parts in correct order to make a meaningful sentence.\n(a) medical challenges\n(b) one of the biggest\n(c) Covid-19 was\n(d) faced by the country",
        "options": ["(1) (d) (c) (b) (a)", "(2) (c) (b) (a) (d)", "(3) (a) (b) (c) (d)", "(4) (b) (c) (d) (a)"],
        "correctAnswer": "(2)", "explanation": "The correct order is: (c) Covid-19 was (subject + verb) (b) one of the biggest (superlative phrase) (a) medical challenges (noun phrase) (d) faced by the country (participle phrase modifying challenges)."
    },
    {
        "id": 128, "subject": "English", "topic": "Grammar",
        "text": "Fill in the blank with correct preposition.\nIt has been raining continuously ______ Monday.",
        "options": ["(1) from", "(2) for", "(3) since", "(4) of"],
        "correctAnswer": "(3)", "explanation": "'Since' is used with a specific point in time in the past (Monday) to indicate the starting point of an action that continues to the present. 'For' is used with a duration of time (e.g., for three days)."
    },
    {
        "id": 129, "subject": "English", "topic": "Grammar",
        "text": "Fill in the blank with correct preposition.\nIt is impossible ______ agree with you on this point.",
        "options": ["(1) off", "(2) for", "(3) from", "(4) to"],
        "correctAnswer": "(4)", "explanation": "The structure requires an infinitive verb form after 'impossible'. The infinitive is formed with 'to + base verb', so 'to agree' is correct."
    },
    {
        "id": 130, "subject": "English", "topic": "Grammar",
        "text": "Identify the correct tense form for the underlined parts in the given sentence.\nHe who <u>pays</u> the piper, <u>calls</u> the tune.",
        "options": ["(1) Simple Present Tense", "(2) Present Perfect Tense", "(3) Present Continuous Tense", "(4) Present Perfect Continuous Tense"],
        "correctAnswer": "(1)", "explanation": "This is a proverb stating a general truth. Both verbs, 'pays' and 'calls', are in their base form with an '-s' for the third-person singular subject ('He'), which is characteristic of the Simple Present Tense."
    },
    {
        "id": 131, "subject": "English", "topic": "Grammar",
        "text": "Identify the correct tense form for the underlined parts in the given sentence.\nWhy <u>have they been angry</u> with me for a long time?",
        "options": ["(1) Past Tense", "(2) Present Perfect Tense", "(3) Past Perfect Tense", "(4) Simple Present Tense"],
        "correctAnswer": "(2)", "explanation": "The structure 'have + been' is used in the Present Perfect Tense to describe a state that began in the past and continues into the present. The phrase 'for a long time' confirms this continuous state."
    },
    {
        "id": 132, "subject": "English", "topic": "Grammar",
        "text": "Identify the part which contains an error.\n'Aesop's Fables' are / a collection of stories / meant to be read / by children.",
        "options": ["(1) 'Aesop's Fables' are", "(2) a collection of stories", "(3) meant to be read", "(4) by children."],
        "correctAnswer": "(1)", "explanation": "The title of a book, even if it is plural in form (like 'Fables'), is treated as a single entity (a singular subject). Therefore, it requires a singular verb. It should be ''Aesop's Fables' is...'."
    },
    {
        "id": 133, "subject": "English", "topic": "Grammar",
        "text": "Identify the part which contains an error.\nHardly I had / reached the station / when the train / started.",
        "options": ["(1) Hardly I had", "(2) reached the station", "(3) when the train", "(4) started."],
        "correctAnswer": "(1)", "explanation": "When a sentence begins with a negative adverb like 'Hardly', 'Scarcely', or 'No sooner', it requires an inversion of the subject and the auxiliary verb. The correct structure is 'Hardly had I reached...'."
    },
    {
        "id": 134, "subject": "English", "topic": "Vocabulary",
        "text": "Choose the word nearest in meaning to the given word.\nRELINQUISH",
        "options": ["(1) Adopt", "(2) Hate", "(3) Discard", "(4) Frown"],
        "correctAnswer": "(3)", "explanation": "To 'relinquish' means to voluntarily cease to keep or claim; to give up. 'Discard' (get rid of) is the closest synonym in meaning."
    },
    {
        "id": 135, "subject": "English", "topic": "Vocabulary",
        "text": "Choose the word nearest in meaning to the given word.\nASSENT",
        "options": ["(1) internalise", "(2) adopt", "(3) welcome", "(4) agree"],
        "correctAnswer": "(4)", "explanation": "'Assent' means the expression of approval or agreement. 'Agree' is a direct synonym."
    },
    {
        "id": 136, "subject": "English", "topic": "Vocabulary",
        "text": "Choose the word opposite in meaning to the given word.\nHUMBLE",
        "options": ["(1) Confident", "(2) Proud", "(3) Aggressive", "(4) Dominating"],
        "correctAnswer": "(2)", "explanation": "'Humble' means having or showing a modest or low estimate of one's own importance. The direct opposite is 'proud', which means having a high opinion of oneself."
    },
    {
        "id": 137, "subject": "English", "topic": "Vocabulary",
        "text": "Choose the word opposite in meaning to the given word.\nTHRIFTY",
        "options": ["(1) Miserly", "(2) Stingy", "(3) Extravagant", "(4) Generous"],
        "correctAnswer": "(3)", "explanation": "'Thrifty' means using money and other resources carefully and not wastefully. 'Extravagant' means spending money or using resources recklessly, which is its opposite. 'Miserly' and 'Stingy' are extreme forms of thrift, while 'Generous' is about giving, not spending."
    },
    {
        "id": 138, "subject": "English", "topic": "Grammar",
        "text": "Identify the part of speech of the underlined word.\n<u>Smoking</u> is injurious to health.",
        "options": ["(1) Adjective", "(2) Noun", "(3) Verb", "(4) Conjunction"],
        "correctAnswer": "(2)", "explanation": "In this sentence, 'Smoking' is a gerund (a verb form ending in -ing that functions as a noun). It is acting as the subject of the verb 'is'. Therefore, its part of speech is a Noun."
    },
    {
        "id": 139, "subject": "English", "topic": "Grammar",
        "text": "Change the following sentence from Active Voice to Passive Voice.\nHe placed an order for a cup of tea.",
        "options": ["(1) An order for a cup of tea has been placed by him.", "(2) A cup of tea was ordered by him.", "(3) An order for a cup of tea was placed by him.", "(4) An order for a cup of tea is placed by him."],
        "correctAnswer": "(3)", "explanation": "The active sentence is in the Simple Past tense ('placed'). The passive voice structure for Simple Past is 'was/were + past participle'. The object 'an order for a cup of tea' becomes the subject. Thus, the correct passive form is 'An order for a cup of tea was placed by him.'"
    },
    {
        "id": 140, "subject": "English", "topic": "Grammar",
        "text": "Identify the clause of the underlined part of the sentence.\nThe car <u>that he bought yesterday</u> looks elegant.",
        "options": ["(1) Noun Clause", "(2) Adjective Clause", "(3) Adverb Clause", "(4) Principal Clause"],
        "correctAnswer": "(2)", "explanation": "The underlined clause 'that he bought yesterday' provides more information about the noun 'car' (it specifies which car). Clauses that describe or modify nouns are Adjective Clauses (or relative clauses)."
    },
    {
        "id": 141, "subject": "Maths", "topic": "Number System",
        "text": "In the number 4650423, the sum of the place values of 4 is:",
        "options": ["(1) 4000040", "(2) 400040", "(3) 4000400", "(4) 4004000"],
        "correctAnswer": "(3)", "explanation": "In 4,650,423: \nThe place value of the first 4 is 4 x 1,000,000 = 4,000,000. \nThe place value of the second 4 is 4 x 100 = 400. \nSum = 4,000,000 + 400 = 4,000,400."
    },
    {
        "id": 142, "subject": "Maths", "topic": "Geometry",
        "text": "Which of the following statements is wrong?",
        "options": ["(1) An angle whose measure is 90°, is called right angle.", "(2) An angle whose measure is greater than 90° but less than 180°, is called obtuse angle.", "(3) An angle whose measure is 180°, is called reflex angle.", "(4) An angle whose measure is greater than 0° but less than 90°, is called acute angle."],
        "correctAnswer": "(3)", "explanation": "An angle that measures exactly 180° is called a straight angle. A reflex angle is an angle that is greater than 180° but less than 360°. Therefore, the third statement is wrong."
    },
    {
        "id": 143, "subject": "Maths", "topic": "Measurement",
        "text": "The perimeter of a rectangular park is 5 km, 474 m. If its length is 1 km 782 m, then its breadth is:",
        "options": ["(1) 955 m", "(2) 1005 m", "(3) 905 m", "(4) 950 m"],
        "correctAnswer": "(1)", "explanation": "Perimeter = 2 * (Length + Breadth). First, convert everything to meters. \nPerimeter = 5474 m. Length = 1782 m. \n5474 = 2 * (1782 + Breadth) \n2737 = 1782 + Breadth \nBreadth = 2737 - 1782 = 955 m."
    },
    {
        "id": 144, "subject": "Maths", "topic": "Measurement",
        "text": "A family consumed 38 kg 435 g flour in October, 42 kg 245 g in November and 29 kg 798 g in December. Based on the above, which one of the following statements is not true?",
        "options": ["(1) Total consumption in three months is 110 kg 478 g.", "(2) Consumption in October was 3 kg 810 g less than November.", "(3) Consumption in December was 12 kg 447 g less than November.", "(4) Consumption in December was 7 kg 607 g less than October."],
        "correctAnswer": "(4)", "explanation": "Let's check the statement: Difference between October (38435 g) and December (29798 g) is 38435 - 29798 = 8637 g, which is 8 kg 637 g. The statement says the difference is 7 kg 607 g, which is false."
    },
    {
        "id": 145, "subject": "Maths", "topic": "Geometry",
        "text": "Box A measures 20 cm by 5 cm by 4 cm and box B measures 16 cm by 5 cm by 3 cm. Based on this information, which one of the following statements is correct?",
        "options": ["(1) Box B has greater volume.", "(2) Volume of box A and box B are equal.", "(3) Difference of volume of box A and box B is 5 cm³.", "(4) Box A has greater volume."],
        "correctAnswer": "(4)", "explanation": "Volume of Box A = 20 * 5 * 4 = 400 cm³. \nVolume of Box B = 16 * 5 * 3 = 240 cm³. \nSince 400 > 240, Box A has a greater volume."
    },
    {
        "id": 146, "subject": "Maths", "topic": "Number System",
        "text": "Using digits 4, 0, 9, 8 form the largest and smallest four-digit number (repetition is not allowed). The sum of these two numbers is:",
        "options": ["(1) 13029", "(2) 13929", "(3) 13829", "(4) 13938"],
        "correctAnswer": "(2)", "explanation": "Largest number: Arrange digits in descending order: 9840. \nSmallest number: Arrange digits in ascending order, but 0 cannot be the first digit. So, the smallest is 4089. \nSum = 9840 + 4089 = 13929."
    },
    {
        "id": 147, "subject": "Maths", "topic": "Time",
        "text": "In a school, after prayer classes start at 8:25 am. If each period is of 35 minutes, then the fourth period will start at:",
        "options": ["(1) 10:05 am", "(2) 9:35 am", "(3) 10:00 am", "(4) 10:10 am"],
        "correctAnswer": "(4)", "explanation": "1st period starts: 8:25 am (ends 9:00 am) \n2nd period starts: 9:00 am (ends 9:35 am) \n3rd period starts: 9:35 am (ends 10:10 am) \nTherefore, the 4th period will start at 10:10 am."
    },
    {
        "id": 148, "subject": "Maths", "topic": "Fractions",
        "text": "Which of the following fractions is in its lowest terms?",
        "options": ["(1) 28/79", "(2) 31/186", "(3) 9/156", "(4) 57/152"],
        "correctAnswer": "(1)", "explanation": "A fraction is in its lowest terms if the numerator and denominator have no common factors other than 1. \n- 31/186: 186 is divisible by 31 (186 = 31 * 6). \n- 9/156: Both are divisible by 3. \n- 57/152: Both are divisible by 19 (57=3*19, 152=8*19). \n- 28/79: 28 has factors 2, 4, 7, 14. 79 is a prime number. They have no common factors."
    },
    {
        "id": 149, "subject": "Maths", "topic": "Geometry",
        "text": "Choose the odd one out from the given images related to a circle.",
        "options": ["(1) tangent", "(2) secant", "(3) radius", "(4) chord"],
        "correctAnswer": "(1)", "explanation": "A radius, chord, and secant all intersect the circle's interior at one or two points. A tangent is a line that touches the circle at exactly one point from the outside. This makes it distinct."
    },
    {
        "id": 150, "subject": "Reasoning", "topic": "Counting Figures",
        "text": "Count the number of rectangles in the given figure.",
        "options": ["(1) 8", "(2) 9", "(3) 7", "(4) 10"],
        "correctAnswer": "(2)", "explanation": "This question requires a figure. Assuming a standard 2x2 grid is presented (which is a common pattern for '9' rectangles), the count is 9 (4 small squares, 4 rectangles of 2 squares, 1 large square)."
    },
    {
        "id": 151, "subject": "Maths", "topic": "Arithmetic",
        "text": "Supriya bought two shirts for ₹ 724.38 per piece and three cardigans for ₹ 936.46 per piece. How much did she have to pay?",
        "options": ["(1) ₹ 4257.04", "(2) ₹ 4285.34", "(3) ₹ 4268.24", "(4) ₹ 4258.14"],
        "correctAnswer": "(4)", "explanation": "Cost of shirts = 2 * 724.38 = ₹ 1448.76. \nCost of cardigans = 3 * 936.46 = ₹ 2809.38. \nTotal cost = 1448.76 + 2809.38 = ₹ 4258.14."
    },
    {
        "id": 152, "subject": "Maths", "topic": "Geometry",
        "text": "Which of the following statements is wrong?",
        "options": ["(1) All the faces of a cuboid are identical.", "(2) A cylinder has two circular faces.", "(3) A cone has one vertex.", "(4) A sphere has no vertex."],
        "correctAnswer": "(1)", "explanation": "A cuboid has 6 rectangular faces, but only the opposite faces are identical. All faces are identical only in the special case of a cube. The other statements are correct."
    },
    {
        "id": 153, "subject": "Reasoning", "topic": "Number Series",
        "text": "The next number in the series, 1, 50, 100, 5000, 10000, ______ is:",
        "options": ["(1) 50000", "(2) 500000", "(3) 100000", "(4) 1000000"],
        "correctAnswer": "(2)", "explanation": "The pattern is an alternating multiplication: \n1 * 50 = 50 \n50 * 2 = 100 \n100 * 50 = 5000 \n5000 * 2 = 10000 \nThe next step is 10000 * 50 = 500,000."
    },
    {
        "id": 154, "subject": "Maths", "topic": "Time and Distance",
        "text": "Pappan walks 4 km 812 m in 2 hours. In 5 hours he will travel a distance of:",
        "options": ["(1) 11 km 930 m", "(2) 12 km 300 m", "(3) 12 km 30 m", "(4) 11 km 630 m"],
        "correctAnswer": "(3)", "explanation": "First, find the speed per hour. \nDistance = 4812 m. Time = 2 hours. \nSpeed = 4812 / 2 = 2406 meters per hour. \nDistance in 5 hours = 2406 * 5 = 12030 meters. \nConverting back to km and m: 12030 m = 12 km and 30 m."
    },
    {
        "id": 155, "subject": "Maths", "topic": "Measurement",
        "text": "Kunti has 3 buffaloes. On Monday, they gave 9.488 L, 11.375 L and 12.643 L of milk. She sold 29.250 L milk to her regular customers. The milk left with her is:",
        "options": ["(1) 5.156 L", "(2) 3.956 L", "(3) 4.250 L", "(4) 4.256 L"],
        "correctAnswer": "(4)", "explanation": "Total milk produced = 9.488 + 11.375 + 12.643 = 33.506 L. \nMilk sold = 29.250 L. \nMilk left = 33.506 - 29.250 = 4.256 L."
    },
    {
        "id": 156, "subject": "Maths", "topic": "Number System",
        "text": "The least number of five digits which is exactly divisible by 75 is:",
        "options": ["(1) 10050", "(2) 10025", "(3) 10015", "(4) 10040"],
        "correctAnswer": "(1)", "explanation": "The smallest 5-digit number is 10000. \nDivide 10000 by 75: 10000 / 75 = 133 with a remainder of 25. \nThis means 10000 is 25 more than a multiple of 75. To find the next multiple, we need to add (75 - 25) = 50 to 10000. \nSo, the number is 10000 + 50 = 10050."
    },
    {
        "id": 157, "subject": "Maths", "topic": "Measurement",
        "text": "Which of the following statements is false?",
        "options": ["(1) To convert dam into dm, you have to multiply by 100.", "(2) To convert mL into dL, you have to divide by 100.", "(3) To convert hL into L, you have to multiply by 10.", "(4) To convert kg into dag, you have to multiply by 100."],
        "correctAnswer": "(3)", "explanation": "Let's check each statement: \n1. 1 dam = 10 m, 1 m = 10 dm -> 1 dam = 100 dm (True). \n2. 1 dL = 100 mL -> To convert mL to dL, divide by 100 (True). \n3. 1 hL (hectolitre) = 100 L (litres) -> To convert hL to L, multiply by 100, not 10 (False). \n4. 1 kg = 1000 g, 1 dag = 10 g -> 1 kg = 100 dag -> To convert kg to dag, multiply by 100 (True)."
    },
    {
        "id": 158, "subject": "Maths", "topic": "Number System",
        "text": "Roman numerals: CXIX, XCIX, CXXI, CIX and CXX can be written in increasing order as:",
        "options": ["(1) XCIX, CIX, CXIX, CXX, CXXI", "(2) XCIX, CXIX, CIX, CXXI, CXX", "(3) CIX, CXIX, CXX, XCIX, CXXI", "(4) CXXI, CXX, CXIX, CIX, XCIX"],
        "correctAnswer": "(1)", "explanation": "First, convert the Roman numerals to Arabic numerals: \nXCIX = 99 \nCIX = 109 \nCXIX = 119 \nCXX = 120 \nCXXI = 121 \nIn increasing order, this is 99, 109, 119, 120, 121, which corresponds to XCIX, CIX, CXIX, CXX, CXXI."
    },
    {
        "id": 159, "subject": "Maths", "topic": "Measurement",
        "text": "A hall is 42 m long and its breadth is 1/3 rd of its length. Its floor is to be covered with tiles of 50 cm length and 30 cm breadth. The required number of tiles will be:",
        "options": ["(1) 3290", "(2) 3620", "(3) 3920", "(4) 3260"],
        "correctAnswer": "(3)", "explanation": "Hall length = 42 m. \nHall breadth = (1/3) * 42 = 14 m. \nArea of hall = 42 m * 14 m = 588 sq m. \nTile length = 50 cm = 0.5 m. \nTile breadth = 30 cm = 0.3 m. \nArea of one tile = 0.5 m * 0.3 m = 0.15 sq m. \nNumber of tiles = Area of hall / Area of one tile = 588 / 0.15 = 3920."
    },
    {
        "id": 160, "subject": "Maths", "topic": "Data Interpretation",
        "text": "If the savings of a family is ₹750, then what is the monthly income? (Pie chart needed)",
        "options": ["(1) ₹ 21000", "(2) ₹ 20000", "(3) ₹ 12000", "(4) ₹ 9000"],
        "correctAnswer": "(4)", "explanation": "This question requires a pie chart. Assuming a standard pie chart where 'Savings' corresponds to a 30° angle (or 1/12th of the total), then: \n(1/12) * Total Income = ₹750 \nTotal Income = 750 * 12 = ₹9000."
    },
    {
        "id": 161, "subject": "Science", "topic": "Chemistry",
        "text": "Below are two statements. Read them carefully and choose the correct option.\nStatement (I) : Carbon Dioxide can be stored as a liquid in cylinder at low pressure.\nStatement (II) : CO2 expands enormously in volume and cools, when released from the cylinder.",
        "options": ["(1) Both statement (I) and statement (II) are true.", "(2) Both statement (I) and statement (II) are false.", "(3) Statement (I) is true but Statement (II) is false.", "(4) Statement (I) is false but Statement (II) is true."],
        "correctAnswer": "(4)", "explanation": "Statement (I) is false; Carbon Dioxide is stored as a liquid under very high pressure, not low pressure. Statement (II) is true; when the high pressure is released, the liquid CO2 rapidly turns into a gas, expands, and cools down significantly (Joule-Thomson effect), forming solid dry ice."
    },
    {
        "id": 162, "subject": "Science", "topic": "Materials",
        "text": "Such plastic which gets deformed easily on heating and can be bent easily, are called:",
        "options": ["(1) Thermosetting plastic", "(2) Thermoplastic", "(3) Rayon plastic", "(4) Nylon plastic"],
        "correctAnswer": "(2)", "explanation": "This is the definition of a thermoplastic. They can be repeatedly softened by heating and hardened by cooling. Examples include polythene and PVC. Thermosetting plastics, once set, cannot be reshaped by heating."
    },
    {
        "id": 163, "subject": "Science", "topic": "Biology",
        "text": "Assertion (A) : Pasteurized milk can be used without boiling.\nReason (R) : Pasteurized milk is free from harmful microorganisms.",
        "options": ["(1) Both (A) and (R) are true and (R) is the correct explanation of (A).", "(2) Both (A) and (R) are true but (R) is not the correct explanation of (A).", "(3) (A) is true but (R) is false.", "(4) (A) is false but (R) is true."],
        "correctAnswer": "(1)", "explanation": "Pasteurization is a process of heating milk to a specific temperature for a set period to kill harmful bacteria (Reason R). Because it is free from these harmful microbes, it is safe to consume without further boiling (Assertion A). Thus, R is the correct explanation for A."
    },
    {
        "id": 164, "subject": "Science", "topic": "Biology",
        "text": "Which of the following statements are true about Lactobacillus Bacteria?\n(A) It is a rod shaped bacteria.\n(B) It helps in setting of curd.\n(C) It is also used in making cheese and pickles.\n(D) It can be seen through naked eyes.",
        "options": ["(1) Only (A) and (B)", "(2) Only (A), (B) and (D)", "(3) Only (B), (C) and (D)", "(4) Only (A), (B) and (C)"],
        "correctAnswer": "(4)", "explanation": "Lactobacillus is a rod-shaped bacterium (A) that promotes the formation of curd from milk (B) and is used in the fermentation of other foods like cheese and pickles (C). However, being a bacterium, it is microscopic and cannot be seen with the naked eye (D is false)."
    },
    {
        "id": 165, "subject": "EVS", "topic": "Agriculture",
        "text": "Which of the following statements are true in the context of irrigation?\n(A) The supply of water to crops at regular intervals is called irrigation.\n(B) The time and frequency of irrigation vary from crop to crop and soil to soil.\n(C) In summer, the frequency of watering is lower.\n(D) The rate of evaporation of water from soil is lower in summer season.",
        "options": ["(1) Only (A) and (C)", "(2) Only (B) and (C)", "(3) Only (A), (C) and (D)", "(4) Only (A) and (B)"],
        "correctAnswer": "(4)", "explanation": "(A) and (B) are correct definitions and principles of irrigation. (C) is false because the frequency of watering is higher in summer due to increased evaporation. (D) is false because the rate of evaporation is higher in summer due to higher temperatures."
    },
    {
        "id": 166, "subject": "EVS", "topic": "Agriculture",
        "text": "Which of the following is true about crop rotation?\n(A) It is a method of growing different crops alternately.\n(B) It helps in the replenishment of the soil with nutrients.\n(C) Farmers in Northern India use this as a method to replenish soil with nitrogen.\n(D) It does not help in controlling pests and weeds.",
        "options": ["(1) Only (A) and (B)", "(2) Only (B) and (C)", "(3) Only (C) and (D)", "(4) Only (A), (B) and (C)"],
        "correctAnswer": "(4)", "explanation": "(A), (B), and (C) are all true statements about crop rotation. It involves growing different crops alternately, which helps replenish soil nutrients (e.g., planting legumes to fix nitrogen), a practice common in Northern India. (D) is false because crop rotation is a key method for naturally controlling pests and weeds that are specific to certain crops."
    },
    {
        "id": 167, "subject": "Science", "topic": "Biology",
        "text": "During heavy exercise, we get cramps in the legs due to the accumulation of:",
        "options": ["(1) Carbon dioxide", "(2) Lactic acid", "(3) Alcohol", "(4) Water"],
        "correctAnswer": "(2)", "explanation": "When muscles work hard during heavy exercise, they may not get enough oxygen for aerobic respiration. They switch to anaerobic respiration, which breaks down glucose into lactic acid. The accumulation of lactic acid in the muscle cells causes cramps."
    },
    {
        "id": 168, "subject": "EVS", "topic": "Safety",
        "text": "Suppose you are stuck in a storm accompanied by lightning, which of the following places will be the most suitable for you to take shelter?",
        "options": ["(1) Under Big trees", "(2) Under Small trees", "(3) Open storage shed", "(4) Inside a car or bus"],
        "correctAnswer": "(4)", "explanation": "A hard-topped car or bus acts as a Faraday cage, conducting electricity around the occupants on the outside of the metal body and safely to the ground. Trees are extremely dangerous as they are often the tallest objects and attract lightning. An open shed offers minimal protection."
    },
    {
        "id": 169, "subject": "Science", "topic": "Biology",
        "text": "Assertion (A) : Polar Bears have a very strong sense of smell.\nReason (R) : The strong sense of smell helps the bears to catch their prey.",
        "options": ["(1) Both (A) and (R) are true and (R) is the correct explanation of (A).", "(2) Both (A) and (R) are true but (R) is not the correct explanation of (A).", "(3) (A) is true but (R) is false.", "(4) (A) is false but (R) is true."],
        "correctAnswer": "(1)", "explanation": "Polar bears have an excellent and highly developed sense of smell (Assertion A), which is a crucial adaptation for survival in the Arctic. They use it to locate seals (their primary prey) from great distances, often from nearly 20 miles away (Reason R). Thus, R correctly explains the adaptive advantage of A."
    },
    {
        "id": 170, "subject": "Science", "topic": "Biology",
        "text": "Choose the correct equation.",
        "options": ["(1) Alimentary canal - Associated glands = Digestive system.", "(2) Alimentary canal + Digestive system = Associated glands.", "(3) Digestive system + Associated glands = Alimentary canal.", "(4) Digestive system = Alimentary canal + Associated glands."],
        "correctAnswer": "(4)", "explanation": "The human digestive system is composed of two main parts: the alimentary canal (the long tube through which food passes, including the mouth, esophagus, stomach, intestines) and the associated glands (like salivary glands, liver, and pancreas) that produce enzymes and juices for digestion."
    },
    {
        "id": 171, "subject": "GK", "topic": "Law/Policy",
        "text": "Below are a few statements related to the Right to Forest Act, 2006. Choose the correct answer.\n(A) This law states that people who have been living in the forests for at least 50 years, have a right over the forest land.\n(B) The work of protecting the forest should be done by the Gram Sabha of their village.",
        "options": ["(1) Only (A)", "(2) Only (B)", "(3) Both (A) and (B)", "(4) Neither (A) nor (B)"],
        "correctAnswer": "(2)", "explanation": "The Forest Rights Act, 2006 grants land rights to forest dwellers who have been living there for at least 25 years (not 50 years), so statement (A) is incorrect. The act empowers the Gram Sabha (village assembly) to manage and protect community forest resources, making statement (B) correct."
    },
    {
        "id": 172, "subject": "Science", "topic": "Physics",
        "text": "Assertion (A) : People in a spaceship feel weightless.\nReason (R) : The spaceship revolves around the Earth.",
        "options": ["(1) Both (A) and (R) are true and (R) is the correct explanation of (A).", "(2) Both (A) and (R) are true but (R) is not the correct explanation of (A).", "(3) (A) is true but (R) is false.", "(4) (A) is false but (R) is true."],
        "correctAnswer": "(2)", "explanation": "Both statements are true. Astronauts in a spaceship orbiting the Earth do feel weightless (A), and the spaceship does revolve around the Earth (R). However, the reason for weightlessness is not simply the revolution; it's because the spaceship and everything in it are in a constant state of freefall towards the Earth. Since everything is falling at the same rate, they feel weightless relative to the spaceship."
    },
    {
        "id": 173, "subject": "EVS", "topic": "Culture",
        "text": "I can make snakes dance by playing the ‘been’. I have learnt this art from my community members. These people/members are called ______.",
        "options": ["(1) Duboia", "(2) Afai", "(3) Kalbeliyas", "(4) Hunters"],
        "correctAnswer": "(3)", "explanation": "The Kalbeliya are a nomadic community from Rajasthan, India, who are traditionally known as snake charmers and traders. The 'been' is their traditional musical instrument used to 'charm' snakes."
    },
    {
        "id": 174, "subject": "EVS", "topic": "Plants",
        "text": "A tree is found in Australia. It has very few leaves. Its roots go deep into the ground until they reach water. This water is stored in the tree trunk. Local people use a thin pipe to drink this water. What is this plant known as?",
        "options": ["(1) Desert Oak", "(2) Pine", "(3) Cedar", "(4) Cactus"],
        "correctAnswer": "(1)", "explanation": "This is a classic description of the Desert Oak, a tree native to the arid regions of Australia, known for its deep roots and water-storing trunk, a feature utilized by Indigenous Australians."
    },
    {
        "id": 175, "subject": "EVS", "topic": "Food",
        "text": "Some flowers are also used as vegetables. Choose the correct option from the following:\n(A) Kachnar flower\n(B) Sahjan flower\n(C) Banana flower\n(D) Rafflesia flower",
        "options": ["(1) (A) and (B)", "(2) (B) and (C)", "(3) (A), (B) and (C)", "(4) (A), (B) and (D)"],
        "correctAnswer": "(3)", "explanation": "Kachnar (Bauhinia) flowers, Sahjan (Moringa/Drumstick) flowers, and Banana flowers are all commonly cooked and eaten as vegetables in various parts of India. Rafflesia, the largest flower in the world, is parasitic and not edible."
    },
    {
        "id": 176, "subject": "History", "topic": "Early Human Civilization",
        "text": "Arrange the following in the correct sequence:\n(A) After a lot of effort... people learnt to make pots.\n(B) People also discovered that clay pots could be made stronger by baking them in fire.\n(C) They (people) started feeling the need to store and cook food.\n(D) Many-many years ago, there was a time when people had no pots.",
        "options": ["(1) (A), (B), (C), (D)", "(2) (D), (C), (A), (B)", "(3) (C), (D), (B), (A)", "(4) (D), (A), (C), (B)"],
        "correctAnswer": "(2)", "explanation": "The logical historical progression is: \n(D) First, there was a time with no pots. \n(C) Then, the development of agriculture created a need for storage. \n(A) This need drove the innovation of making clay pots. \n(B) Finally, they improved the technology by baking the pots to make them stronger."
    },
    {
        "id": 177, "subject": "EVS", "topic": "Geography",
        "text": "You have gone to travel to a place where sea fish cooked in coconut oil is being served to you. Tell the place where you have gone to travel.",
        "options": ["(1) West Bengal", "(2) Goa", "(3) Kashmir", "(4) Mizoram"],
        "correctAnswer": "(2)", "explanation": "Goa is a coastal state famous for its seafood cuisine. The use of coconut oil is a defining characteristic of Goan and other South Indian coastal cooking. In contrast, a place like Kashmir is known for fish cooked in mustard oil."
    },
    {
        "id": 178, "subject": "Pedagogy", "topic": "Environment Education",
        "text": "Statement (I) : Children should be encouraged to make friends with a tree, watering it, looking after it, noting its growth etc.\nStatement (II) : If the children are encouraged to make friends with a tree, it will develop a concern for the environment.",
        "options": ["(1) Both statement (I) and statement (II) are true.", "(2) Both statement (I) and statement (II) are false.", "(3) Statement (I) is true but Statement (II) is false.", "(4) Statement (I) is false but Statement (II) is true."],
        "correctAnswer": "(1)", "explanation": "Statement (I) describes a sound pedagogical practice for environmental education. Statement (II) provides the correct rationale for this practice. By forming a personal connection and sense of responsibility for a living thing (a tree), children are likely to develop a broader concern and respect for the environment."
    },
    {
        "id": 179, "subject": "Science", "topic": "Chemistry",
        "text": "Which of the following solutions is used to check for the presence of 'starch' in food products?",
        "options": ["(1) Caustic Soda", "(2) Copper Sulphate", "(3) Iodine", "(4) Water"],
        "correctAnswer": "(3)", "explanation": "A dilute iodine solution is the standard chemical indicator for starch. When a few drops of iodine solution are added to a food item containing starch, it turns a blue-black color, confirming the presence of starch."
    },
    {
        "id": 180, "subject": "Science", "topic": "Physics/Geography",
        "text": "Statement (I) : At sufficient heights, the air becomes so cool that the water vapour present in it condenses to form tiny droplets of water.\nStatement (II) : These tiny droplets, that remain floating in the air, appear to us as clouds.",
        "options": ["(1) Statement (I) and Statement (II) both are true.", "(2) Statement (I) and Statement (II) both are false.", "(3) Statement (I) is true but Statement (II) is false.", "(4) Statement (I) is false but Statement (II) is true."],
        "correctAnswer": "(1)", "explanation": "Both statements accurately describe the process of cloud formation. As warm, moist air rises, it cools, and the water vapor condenses into tiny water droplets (Statement I). A massive collection of these floating droplets forms a cloud that is visible to us (Statement II)."
    }
]

# --- App Styling ---

def get_css():
    """Returns a string containing the custom CSS for the app."""
    return """
    <style>
        :root {
            --primary-blue: #3498db;
            --vibrant-green: #27ae60;
            --vibrant-red: #e74c3c;
            --purple-marked: #8e44ad;
            --grey-unvisited: #bdc3c7;
            --text-dark: #34495e;
        }
        .stApp > header { background-color: transparent; }
        .stApp { margin: auto; font-family: 'Roboto', sans-serif; }
        .exam-header {
            display: flex; justify-content: space-between; align-items: center;
            padding: 0.5rem 1rem; background-color: var(--primary-blue); color: white;
            position: sticky; top: 0; z-index: 999; border-radius: 5px; margin-bottom: 1rem;
        }
        .exam-header .title { font-size: 1.5rem; font-weight: bold; }
        .exam-header .timer-box {
            background: rgba(255,255,255,.2); padding: .5rem 1rem; border-radius: 4px;
            font-family: monospace; font-size: 1.2rem;
        }
        .question-text {
            font-size: 1.15rem; line-height: 1.7; margin-bottom: 2rem;
            white-space: pre-wrap; color: var(--text-dark);
        }
        div[data-testid="stRadio"] > label {
            padding: 0.75rem 1rem !important; border: 1px solid #dce4ec !important;
            border-radius: 5px !important; margin-bottom: 1rem !important; display: block !important;
        }
        div[data-testid="stRadio"] > label:hover { background-color: #f1f8ff; }
        .result-box {
             border: 1px solid #dce4ec; border-radius: 8px;
             padding: 1.5rem; margin-bottom: 1rem;
        }
        .result-box.correct { border-left: 5px solid var(--vibrant-green); }
        .result-box.incorrect { border-left: 5px solid var(--vibrant-red); }
        .result-box.unattempted { border-left: 5px solid var(--grey-unvisited); }
        .correct-answer { background-color: #eaf8f0; border-radius: 4px; padding: 0.5rem; }
        .user-answer.incorrect { background-color: #fdedec; border-radius: 4px; padding: 0.5rem; }
    </style>
    """

# --- State Management and Helper Functions ---

def process_raw_data(raw_data):
    processed_questions = []
    section_map = {}
    
    def subject_normalizer(subject):
        if subject == "Pedagogy": return "Perspectives on Education and Leadership"
        if subject in ["GK", "History", "Polity", "Geography", "Science", "Current Affairs"]: return "General Awareness"
        subject_to_section = {
            "Reasoning": "Reasoning Ability", "Computer Science": "Computer Literacy",
            "English": "General English", "Hindi": "General Hindi",
            "Maths": "Mathematics", "EVS": "Environmental Studies"
        }
        return subject_to_section.get(subject, subject)

    for q in raw_data:
        section_name = subject_normalizer(q['subject'])
        if section_name not in section_map:
            section_map[section_name] = []
        section_map[section_name].append(q)

    section_order = [
        "General English", "General Hindi", "General Awareness", "Reasoning Ability", 
        "Computer Literacy", "Perspectives on Education and Leadership", "Mathematics", 
        "Environmental Studies"
    ]
    
    global_index = 0
    for section_name in section_order:
        if section_name in section_map:
            for q in section_map[section_name]:
                try:
                    correct_index = [i for i, opt in enumerate(q['options']) if opt.startswith(q['correctAnswer'])][0]
                except IndexError:
                    correct_index = -1
                processed_questions.append({
                    "global_index": global_index, "question_num": global_index + 1,
                    "section": section_name, "text": q['text'],
                    "options": [opt.split(')', 1)[1].strip() for opt in q['options']],
                    "correct_index": correct_index, "explanation": q['explanation'],
                    "status": "not-visited", "user_answer": None
                })
                global_index += 1
    return processed_questions, section_order

def initialize_state():
    if 'questions' not in st.session_state:
        st.session_state.questions, st.session_state.section_order = process_raw_data(RAW_QUIZ_DATA)
        st.session_state.current_question_index = 0
        st.session_state.view = 'quiz'
        st.session_state.start_time = time.time()
        st.session_state.score_submitted = False
        st.session_state.show_leaderboard = False

# --- Leaderboard Functions ---

def submit_score_to_leaderboard(name, score, total, time_taken):
    if LEADERBOARD_API_URL == "PASTE_YOUR_GOOGLE_APPS_SCRIPT_URL_HERE":
        st.warning("Leaderboard URL not configured. Score not submitted.")
        return

    payload = {
        "name": name, "score": score, "total": total,
        "timeTaken": int(time_taken), "examId": EXAM_CONFIG['examId']
    }
    try:
        response = requests.post(LEADERBOARD_API_URL, data=json.dumps(payload), headers={'Content-Type': 'application/json'})
        if response.status_code == 200:
            st.toast("Score submitted to leaderboard successfully!")
            st.session_state.score_submitted = True
        else:
             # Handle redirects from Google Apps Script
            if 300 <= response.status_code < 400 and 'Location' in response.headers:
                final_response = requests.get(response.headers['Location'])
                if final_response.status_code == 200:
                     st.toast("Score submitted to leaderboard successfully!")
                     st.session_state.score_submitted = True
                else:
                    st.error(f"Failed to submit score after redirect. Status: {final_response.status_code}")
            else:
                 st.error(f"Failed to submit score. Status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred while submitting score: {e}")

def fetch_leaderboard():
    if LEADERBOARD_API_URL == "PASTE_YOUR_GOOGLE_APPS_SCRIPT_URL_HERE":
        return None, "Leaderboard URL is not configured."
    
    try:
        url = f"{LEADERBOARD_API_URL}?examId={EXAM_CONFIG['examId']}&t={time.time()}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if 'leaderboard' in data and data['leaderboard']:
            return data['leaderboard'], None
        else:
            return [], "No scores submitted yet. Be the first!"
    except requests.exceptions.RequestException as e:
        return None, f"Could not connect to the leaderboard: {e}"
    except json.JSONDecodeError:
        return None, "Error decoding leaderboard data. The API might be configured incorrectly."

# --- UI Rendering Functions ---

def render_timer_header(time_remaining):
    if st.session_state.view == 'quiz':
        st_autorefresh(interval=1000, key="timer_refresh")
    
    if time_remaining <= 0 and st.session_state.view == 'quiz':
        st.warning("Time's up! Your test has been automatically submitted.")
        st.session_state.view = 'results'
        st.rerun()

    hours, rem = divmod(time_remaining, 3600)
    mins, secs = divmod(rem, 60)
    timer_text = f"{int(hours):02}:{int(mins):02}:{int(secs):02}"

    header_html = f"""
    <div class="exam-header">
        <div class="title">{EXAM_CONFIG['exam_title']}</div>
        <div class="timer-box">{timer_text}</div>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)

def render_palette():
    st.sidebar.title("Question Palette")
    st.sidebar.markdown("---")
    current_q = st.session_state.questions[st.session_state.current_question_index]
    st.sidebar.subheader(f"Section: {current_q['section']}")
    
    questions_in_section = [q for q in st.session_state.questions if q['section'] == current_q['section']]
    cols = st.sidebar.columns(5)
    for i, q in enumerate(questions_in_section):
        col = cols[i % 5]
        q_status = q['status']
        btn_type = "primary" if q['global_index'] == st.session_state.current_question_index else "secondary"
        
        if q_status == 'answered':
            label = f"✅ {q['question_num']}"
        elif q_status == 'not-answered':
            label = f"❌ {q['question_num']}"
        elif q_status == 'marked':
            label = f"⭐ {q['question_num']}"
        else: # not-visited
            label = f"⚪ {q['question_num']}"
        
        col.button(label, key=f"palette_{q['global_index']}", on_click=lambda i=q['global_index']: st.session_state.update(current_question_index=i), type=btn_type)

def render_quiz_view():
    render_palette()
    
    sections = st.session_state.section_order
    current_section = st.session_state.questions[st.session_state.current_question_index]['section']
    
    # Use st.tabs for better section navigation
    selected_tab = st.tabs([s.replace(" ", "\n") for s in sections])

    # This part is a bit tricky; we need to find which tab was clicked.
    # A more direct approach is still using buttons if tabs prove complex for state.
    # Let's stick to columns of buttons for robust state control.
    cols = st.columns(len(sections))
    for i, section_name in enumerate(sections):
        btn_type = "primary" if section_name == current_section else "secondary"
        cols[i].button(section_name, key=f"sec_{section_name}", on_click=lambda s=section_name: st.session_state.update(current_question_index=[q['global_index'] for q in st.session_state.questions if q['section'] == s][0]), type=btn_type)

    st.markdown("---")

    q_index = st.session_state.current_question_index
    question = st.session_state.questions[q_index]
    if question['status'] == 'not-visited':
        question['status'] = 'not-answered'

    with st.container(border=True):
        st.subheader(f"Question {question['question_num']}")
        st.markdown(f"<div class='question-text'>{question['text']}</div>", unsafe_allow_html=True)
        
        default_index = question['user_answer']
        
        def on_radio_change():
            user_choice_text = st.session_state[f'q_radio_{q_index}']
            try:
                user_choice_index = question['options'].index(user_choice_text)
                question['user_answer'] = user_choice_index
                if question['status'] != 'marked':
                    question['status'] = 'answered'
            except ValueError:
                pass

        st.radio(
            "Choose one option:", question['options'],
            index=default_index, key=f'q_radio_{q_index}',
            on_change=on_radio_change, label_visibility="collapsed"
        )
    
    st.markdown("---")
    
    # Navigation Footer
    c1, c2, c3, c4 = st.columns(4)
    if c1.button("Mark for Review & Next", use_container_width=True):
        question['status'] = 'marked'
        st.session_state.current_question_index = (q_index + 1) % len(st.session_state.questions)
        st.rerun()
    if c2.button("Clear Response", use_container_width=True):
        question['user_answer'] = None
        question['status'] = 'not-answered'
        st.rerun()
    if c3.button("Save & Next", type="primary", use_container_width=True):
        st.session_state.current_question_index = (q_index + 1) % len(st.session_state.questions)
        st.rerun()
    if c4.button("Submit Test", use_container_width=True):
        st.session_state.view = 'summary'
        st.rerun()

def render_summary_view():
    st.title("Test Summary")
    st.warning("Please review your attempt before final submission.")

    summary_data = []
    for section_name in st.session_state.section_order:
        section_qs = [q for q in st.session_state.questions if q['section'] == section_name]
        if not section_qs: continue
        summary_data.append({
            "Section": section_name, "Total": len(section_qs),
            "Answered": sum(1 for q in section_qs if q['status'] == 'answered'),
            "Not Answered": sum(1 for q in section_qs if q['status'] == 'not-answered'),
            "Marked": sum(1 for q in section_qs if q['status'] == 'marked'),
            "Not Visited": sum(1 for q in section_qs if q['status'] == 'not-visited')
        })
    st.table(summary_data)
    
    c1, c2, c3 = st.columns([1,2,1])
    if c1.button("⬅️ Back to Test", use_container_width=True):
        st.session_state.view = 'quiz'
        st.rerun()
    if c3.button("🏁 Final Submit", type="primary", use_container_width=True):
        st.session_state.view = 'results'
        st.rerun()

def render_results_view():
    st.title("Performance Report")
    st.balloons()
    
    correct = sum(1 for q in st.session_state.questions if q['user_answer'] == q['correct_index'])
    attempted = sum(1 for q in st.session_state.questions if q['user_answer'] is not None)
    incorrect = attempted - correct
    unattempted = len(st.session_state.questions) - attempted
    score = (correct * EXAM_CONFIG['marksPerCorrect']) - (incorrect * EXAM_CONFIG['marksPerIncorrect'])
    total_marks = len(st.session_state.questions) * EXAM_CONFIG['marksPerCorrect']
    time_taken = time.time() - st.session_state.start_time

    st.subheader("Score Summary")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Final Score", f"{score}/{total_marks}")
    c2.metric("Correct", f"✅ {correct}")
    c3.metric("Incorrect", f"❌ {incorrect}")
    c4.metric("Unattempted", f"⚪ {unattempted}")

    # Leaderboard Submission
    if not st.session_state.score_submitted:
        with st.form("leaderboard_form"):
            st.write("Submit your score to the live leaderboard!")
            user_name = st.text_input("Enter your name:", "Candidate")
            submitted = st.form_submit_button("Submit Score")
            if submitted:
                submit_score_to_leaderboard(user_name, score, total_marks, time_taken)
    
    st.markdown("---")
    
    # Leaderboard Display
    if st.button("🏆 View Live Leaderboard"):
        st.session_state.show_leaderboard = not st.session_state.show_leaderboard

    if st.session_state.show_leaderboard:
        with st.spinner("Fetching latest scores..."):
            leaderboard_data, error_msg = fetch_leaderboard()
            if error_msg:
                st.error(error_msg)
            elif leaderboard_data:
                # Format for better display
                display_data = [{
                    'Rank': item.get('rank', i+1), 
                    'Name': item.get('name'), 
                    'Score': item.get('score'), 
                    'Time Taken': item.get('timetaken')} for i, item in enumerate(leaderboard_data)]
                st.dataframe(display_data, use_container_width=True)
    
    st.markdown("---")
    st.subheader("Detailed Question Analysis")
    for q in st.session_state.questions:
        status_icon = "⚪"
        if q['user_answer'] is not None:
            status_icon = "✅" if q['user_answer'] == q['correct_index'] else "❌"
        
        with st.expander(f"{status_icon} Question {q['question_num']}: {q['text'][:50]}..."):
            status_class = "unattempted"
            if q['user_answer'] is not None:
                status_class = "correct" if q['user_answer'] == q['correct_index'] else "incorrect"

            st.markdown(f"<div class='result-box {status_class}'>", unsafe_allow_html=True)
            st.markdown(f"**Q: {q['text']}**")
            
            for i, option in enumerate(q['options']):
                display_option = f"({i+1}) {option}"
                if i == q['correct_index']:
                    st.markdown(f"<div class='correct-answer'><b>{display_option} (Correct Answer)</b></div>", unsafe_allow_html=True)
                elif i == q['user_answer']:
                    st.markdown(f"<div class='user-answer incorrect'>{display_option} (Your Answer)</div>", unsafe_allow_html=True)
                else:
                    st.write(display_option)
            st.info(f"**Explanation:** {q['explanation']}")
            st.markdown("</div>", unsafe_allow_html=True)


# --- Main Application Logic ---

def main():
    st.set_page_config(page_title=EXAM_CONFIG['exam_title'], layout="wide")
    st.markdown(get_css(), unsafe_allow_html=True)

    initialize_state()
    
    total_time = EXAM_CONFIG['totalTimeInSeconds']
    elapsed_time = time.time() - st.session_state.start_time
    time_remaining = max(0, total_time - elapsed_time)

    render_timer_header(time_remaining)
    
    if st.session_state.view == 'quiz':
        render_quiz_view()
    elif st.session_state.view == 'summary':
        render_summary_view()
    elif st.session_state.view == 'results':
        render_results_view()

if __name__ == "__main__":
    main()