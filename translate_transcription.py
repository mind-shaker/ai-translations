import json
import os
import sys

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 translate_transcription.py <input.json> <output.json>")
        sys.exit(1)
        
    input_path = sys.argv[1]
    output_path = sys.argv[2]

    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found.")
        return

    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    original_count = len(data.get('segments', []))
    print(f"Original segment count: {original_count}")

    # --- AGENT AI SURGICAL TRANSLATION START ---
    segments = data.get('segments', [])
    
    # Surgical Mapping of Translations (Preserving Indices)
    # Format: {index: "translated_text"}
    translations_map = {
        0: "Today I will show you how ChatGPT can be turned into real learning tools, not just a translator.",
        1: "And today I will not speak in general terms, but will use specific prompts and requests that you can also reproduce.",
        2: "For today's example, I will show all of this at level A1, but this video is not only for beginners, you will be able to adapt all of this yourself, because we will be building an entire learning system.",
        3: "And you can find ready-made prompts for your level in the pinned comment under the link in my Telegram channel.",
        4: "And our first step is the base.",
        5: "You need to know exactly what level of English you have now.",
        6: "That is, it's not okay to write that I have something between A2 or B1.",
        7: "You need to know your exact level, because then ChatGPT will not be able to create a program specifically for you.",
        8: "It will be either too easy or too hard vice versa.",
        9: "For this case, I have a ready-made prompt for you that you can copy and paste for your chat.",
        10: "I'll read it now.",
        11: "You are an experienced English teacher.",
        12: "Help determine my English level.",
        13: "Create a series of tasks that test vocabulary, grammar, reading comprehension, and speaking.",
        14: "Go step by step, gradually increasing complexity.",
        15: "After my answers, explain what this means for my level.",
        16: "And tell me what it is.",
        17: "And in 20-30 minutes, you will have a real understanding of where you are now and where you need to move next.",
        18: "And then another critically important point, a mistake I see constantly, that people open a lot of chats and try to learn in them.",
        19: "But it is very important to open only one chat and learn specifically in it.",
        20: "Then this chat remembers everything about you.",
        21: "What mistakes you made, what you said wrong, what you already covered, what needs to be reinforced again.",
        22: "And when you open new chats, this memory is not preserved and you kind of go through the same thing again.",
        23: "Therefore, we fix one chat, one teacher.",
        24: "Well, now our second step.",
        25: "Now we will create with you that same teacher who will teach us.",
        26: "And let's read this prompt, but you will be able to copy it later.",
        27: "First explain, then give practice, then repeat, speak simply and clearly.",
        28: "And with this step you do a very important thing.",
        29: "You don't just open another random chat, you create your permanent stable teacher.",
        30: "Well, you've already created your teacher, you gave them a goal.",
        31: "Now we're going to practice.",
        32: "The next step we need to get from them certain ready-made phrases that correspond to our level.",
        33: "What do we write to them?",
        34: "Give me 10 very simple English phrases for level A1 on the topic of meeting people without grammar explanations.",
        35: "See, here you can change both the level and the topic for which you want to get these phrases, but in general, I think the logic is clear.",
        36: "And see what they will send us, I'll add a screenshot here.",
        37: "There they are sending.",
        38: "Good, here are some very simple phrases for level A1 on the topic of meeting people.",
        39: "And there's a list there.",
        40: "Hello, hi, my name is Anna.",
        41: "And so on.",
        42: "In principle, they did their job, they sent you not just words, but entire ready-made phrases.",
        43: "And I think you should already know that you need to learn a language fundamentally not in separate words, but in ready-made language chunks.",
        44: "The next stage we will have listening and a prompt for listening.",
        45: "Read these phrases out loud slowly.",
        46: "And now I will show you how it works.",
        47: "Of course.",
        48: "I will read them clearly and slowly now so it's easy for you to repeat.",
        49: "Ready?",
        50: "Let's go.",
        51: "First.",
        52: "Hello.",
        53: "Second.",
        54: "Hi.",
        55: "Third.",
        56: "My name is Anna.",
        57: "Fourth.",
        58: "I am Anna.",
        59: "Fifth.",
        60: "What is your name?",
        61: "Sixth.",
        62: "Nice to meet you.",
        63: "Seventh.",
        64: "I am from Ukraine.",
        65: "Eighth.",
        66: "Where are you from?",
        67: "Ninth.",
        68: "How are you?",
        69: "Tenth.",
        70: "I am fine.",
        71: "Repeat as many times as needed.",
        72: "If you need, just say and we'll do more.",
        73: "That's it.",
        74: "Look, what's important here.",
        75: "You can listen to this more than once.",
        76: "In fact, I really advise you to listen more than once.",
        77: "What for?",
        78: "So that you fix it in your head, your brain will process it better.",
        79: "And will then be able to recognize it in real speech, in real life.",
        80: "And also will later be able to suggest options for these phrases when you speak English yourself.",
        81: "So listen as much as possible.",
        82: "By the way, regarding how to listen to all this, I'll add a screenshot here now.",
        83: "Of what needs to be pressed to voice what was written.",
        84: "The next step we have is reading.",
        85: "And not just some random reading, but reading specifically what you just worked with.",
        86: "That is, we will once again polish those phrases and expressions that you have both read and heard just now.",
        87: "And what will be our prompt for this.",
        88: "See.",
        89: "Create a monologue story, a text for reading.",
        90: "Of six sentences for level A1 with these phrases.",
        91: "It should sound like natural speech, one paragraph, sentences logically connected, no lists, no separate phrases, so it can be said in one breath.",
        92: "And now I will show you what they created for me.",
        93: "I'm adding a screenshot of their response here.",
        94: "And what to do with this.",
        95: "You can read it out loud to yourself.",
        96: "Maybe even more than once.",
        97: "You can ask them again to voice it through the button I already showed you.",
        98: "And what's important here is that your brain perceives what it heard earlier and starts to recall it.",
        99: "And at this moment you are actually learning.",
        100: "And now we're going to move on to grammar.",
        101: "But I'm not going to ask them now to write the usage rules for me.",
        102: "I'll ask them just to explain it to me simply.",
        103: "And see what we can write to them.",
        104: "Explain very simply.",
        105: "What does 'I am' mean?",
        106: "Without grammar terms and complex explanations.",
        107: "See what they answer me.",
        108: "'I am', 'I am', is what you say about yourself.",
        109: "When you want to say who you are, what you are like, how you feel.",
        110: "You start with 'I am'.",
        111: "And examples from life follow.",
        112: "As for me, the explanation is great.",
        113: "There are no complex terms here.",
        114: "There are no rules, no tenses here.",
        115: "Just logical, clear and wonderful for beginners.",
        116: "Of course, if it's some other level, it will already be a bit more complicated.",
        117: "You'll see all of this in the prompts.",
        118: "But for now, the logic is as follows.",
        119: "Well, and now will be my favorite stage.",
        120: "The stage when we starts talking with our chat.",
        121: "Again, through this button.",
        122: "We have to go into conversation mode with them.",
        123: "And what do we say?",
        124: "Let's make a simple dialog in English with you now for level A1.",
        125: "You are a new person for me and ask me simple questions one by one.",
        126: "Of course, everything is fine.",
        127: "We're starting a simple dialog and I'm asking questions one by one.",
        128: "First question.",
        129: "What's your name?",
        130: "My name is Anastasia.",
        131: "Hello, Anastasia.",
        132: "Where are you from?",
        133: "I'm from Ukraine.",
        134: "I agree.",
        135: "What do you like to do in your free time?",
        136: "I like cooking and working out.",
        137: "Of course.",
        138: "Can you tell me if you are learning English right now?",
        139: "I think you understand that I am learning English right now.",
        140: "Of course.",
        141: "I just wanted to tell you that you're doing well.",
        142: "See you.",
        143: "Here is a prompt for writing.",
        144: "Now I'll show you what they answered me.",
        145: "Adding it.",
        146: "First, they wrote me templates that I can use.",
        147: "Next, they give your turn for you to write them these three sentences.",
        148: "In this case, when you write them your sentences, they will correct you if something is wrong.",
        149: "Or they can just praise you if you wrote everything correctly.",
        150: "Now a very important nuance.",
        151: "After each lesson you must record your progress.",
        152: "You have to help this machine record everything that happened to them.",
        153: "What you will write down for them.",
        154: "Also a prompt.",
        155: "Make a short summary of the lesson, what we covered, what mistakes are repeated to repeat next time.",
        156: "No more than 100 words.",
        157: "See, you can insert all of this both at the end of this lesson and at the beginning of the next one, so that you indeed don't forget what you've already covered and could pay attention to what you need to work on better.",
        158: "And now there will be a very logical question, probably from you.",
        159: "Okay, I practiced this today, but what should I do next?",
        160: "How to do all this on my own?",
        161: "And I'll tell you, you don't need to reinvent the wheel, because I've already invented it for you.",
        162: "You just need to copy this prompt and then move along our already created roadmap.",
        163: "See what a prompt it is.",
        164: "Conduct a daily English lesson for level A1.",
        165: "One lesson, one day.",
        166: "Work in stages.",
        167: "Start with a short review of what we've already covered.",
        168: "Two to three minutes.",
        169: "In the review use the same words and constructions as before.",
        170: "After each step stop and wait for my 'next'.",
        171: "Lesson structure.",
        172: "Short review.",
        173: "Short explanation of a new topic.",
        174: "Eight to ten simple phrases.",
        175: "Read them out loud.",
        176: "Short coherent text.",
        177: "Simple explanation of the meaning of constructions.",
        178: "Short dialog.",
        179: "Three sentences of writing.",
        180: "Speak simply and don't overload.",
        181: "And that's all.",
        182: "ChatGPT will guide you further as a real teacher.",
        183: "I think it's just magic.",
        184: "And concerning these prompts.",
        185: "They are written under a general learning system.",
        186: "If you need some specific topic, or specifically to consider some grammar structure, you can, of course, adjust this.",
        187: "So adapt it.",
        188: "ChatGPT is not a tutor.",
        189: "But with a coolly built system, you'll be able to create a real working trainer out of it.",
        190: "So the main thing here is to create this very system, so that it is not chaotic, but broken down like we broke it down today.",
        191: "Because that's how our brain absorbs everything best.",
        192: "So, if it was useful, interesting, you liked it, I will be very grateful for your support.",
        193: "Please like, comment, subscribe.",
        194: "Well, because I already said that.",
        195: "And I want to remind you that under this video and in the pinned comment you will see a link to my Telegram channel where all prompts for each level will be collected.",
        196: "Bye-bye!"
    }

    for idx, eng_text in translations_map.items():
        if idx < original_count:
            # Surgical translation preservation
            segments[idx]['text'] = eng_text

    # Validation
    final_count = len(data.get('segments', []))
    if original_count != final_count:
        print(f"CRITICAL ERROR: Segment count changed from {original_count} to {final_count}!")
        sys.exit(1)

    # --- AGENT AI SURGICAL TRANSLATION END ---
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Successfully processed translation to {output_path}")

if __name__ == "__main__":
    main()
