# -*- coding: utf-8 -*-
"""
Single source of truth for the family teaching document.
Both build_docx.py and build_pdf.py import DOCUMENT from here and render it.

Block types:
  cover      {title, subtitle, meta:[str,...]}
  heading    {level: 1|2, text}
  para       {text}                          -- text may contain **bold** and *italic*
  callout    {style: "kid"|"business"|"note", label, text}
  image      {path, caption, width_in}
  code       {text}
  bullets    {items:[str,...]}
  numbered   {items:[str,...]}
  glossary   {items:[(term, definition), ...]}
  quiz       {items:[{q, options:[...] or None, answer}]}
  divider    {}
  pagebreak  {}
"""

ASSETS = "assets"

DOCUMENT = [

    {"type": "cover",
     "title": "How Our Robot Answers Business Questions",
     "subtitle": "A family field guide to the Retail SQL Agent",
     "meta": ["Written for two of my favorite people: a curious 10-year-old, "
              "and a sharp business mind.",
              "You don't need to know how to code to understand this book — "
              "just curiosity."]},

    {"type": "heading", "level": 1, "text": "Chapter 1 — What Is This Thing, Really?"},

    {"type": "para", "text":
     "Somewhere on Dad's computer lives a little robot. You type it a question in plain "
     "English — like *\"What were our top 5 products by revenue?\"* — and a few seconds "
     "later it types back a short, honest answer, using real numbers from a real database "
     "of store sales."},

    {"type": "para", "text":
     "That's the whole trick. It doesn't guess. It doesn't make things up. It goes and "
     "looks, every single time, and it tells you exactly what it found — including when "
     "it isn't sure about something."},

    {"type": "callout", "style": "kid", "label": "Kid's Eye View", "text":
     "Think of a robot librarian. You ask it a question, it walks into a giant filing "
     "cabinet full of receipts, pulls out exactly the right ones, counts them up, and "
     "comes back to tell you the answer. It promises never to rip up a receipt, never to "
     "reorganize the cabinet, and never to lie about what it found."},

    {"type": "callout", "style": "business", "label": "Business Lens", "text":
     "This is a natural-language interface over a SQL database. Normally, answering "
     "\"which store had the most returns this month\" means finding someone who knows "
     "SQL, waiting for them to write and run a query, and hoping they interpreted the "
     "question correctly. This agent collapses that round-trip into a single typed "
     "sentence — with a safety layer that guarantees it can only *read* data, never "
     "change it."},

    {"type": "para", "text":
     "It was built as a learning project — a chance to understand, hands-on, how modern "
     "\"AI agents\" are actually put together under the hood, rather than treating them "
     "as magic."},

    {"type": "pagebreak"},
    {"type": "heading", "level": 1, "text": "Chapter 2 — Meet the Team Inside the Robot"},

    {"type": "para", "text":
     "It's tempting to imagine one big brain doing everything. In reality, this robot is "
     "more like a small, well-organized office. Four specialists, each with exactly one "
     "job, hand work to each other in a fixed order — every single time, for every single "
     "question."},

    {"type": "image", "path": "meet_the_team.png",
     "caption": "The four specialists, and the one job each of them is allowed to do.",
     "width_in": 6.6},

    {"type": "callout", "style": "kid", "label": "Kid's Eye View", "text":
     "It's a bit like a relay race. The Writer runs the first leg and hands off the baton "
     "to the Guard, who hands off to the Runner, who hands off to the Narrator. Nobody "
     "skips their leg, and nobody runs someone else's."},

    {"type": "callout", "style": "business", "label": "Business Lens", "text":
     "This is a deliberate design choice called *separation of concerns*. One AI model "
     "drafts the query; a completely separate, non-AI piece of code approves or rejects "
     "it; a database driver executes it; a second AI call turns the result into prose. "
     "No single component can both decide something is safe *and* act on it — the same "
     "principle behind requiring two signatures on a large payment."},

    {"type": "pagebreak"},
    {"type": "heading", "level": 1, "text": "Chapter 3 — Follow a Real Question on Its Journey"},

    {"type": "para", "text":
     "Here's an actual run of the robot, end to end, including a natural follow-up "
     "question — the kind of thing you'd really ask in a conversation."},

    {"type": "image", "path": "question_journey.png",
     "caption": "A real question and a real follow-up, exactly as the agent handled them.",
     "width_in": 6.6},

    {"type": "para", "text":
     "Notice what happened with the follow-up. You didn't have to repeat yourself and say "
     "\"what was the UPI revenue for the Mumbai store\" — you just said *\"and only for "
     "the Mumbai store?\"* and the Writer understood you meant the question right before "
     "it. That's conversation memory: the robot is handed the last few turns of your chat "
     "every time, with the most recent one clearly flagged, so it never has to guess which "
     "question a follow-up belongs to."},

    {"type": "callout", "style": "note", "label": "A Bug We Actually Caught", "text":
     "Early on, when there were several unrelated questions earlier in the conversation, "
     "the Writer sometimes reused the *wrong* one — it would grab an older question's "
     "structure instead of the one right before the follow-up. We caught this by "
     "independently checking the numbers by hand, fixed it by explicitly labeling which "
     "turn was \"most recent,\" and re-tested to confirm it was fixed. That's the human "
     "review step in action — never trust an AI's output for something that matters "
     "without checking it."},

    {"type": "pagebreak"},
    {"type": "heading", "level": 1, "text": "Chapter 4 — The Rules That Keep It Safe"},

    {"type": "para", "text":
     "The single most important design decision in this whole project is about the "
     "Guard. It would have been easier to just tell the AI, in the prompt, \"please only "
     "write safe SELECT queries and never delete anything.\" That's tempting — but it's "
     "not good enough, because an AI model can occasionally misunderstand, get tricked, "
     "or simply have an off moment."},

    {"type": "para", "text":
     "So the Guard isn't AI at all. It's plain, boring, predictable code — the kind that "
     "does the exact same thing every time, forever. It checks, in order:"},

    {"type": "numbered", "items": [
        "Is this exactly one instruction? (Not five instructions hidden in one message.)",
        "Does it start with the word SELECT? (SELECT only *reads* data — it can never "
        "change or delete anything.)",
        "Does it contain any of 12 forbidden words — things like DELETE, DROP, UPDATE, "
        "or ALTER — anywhere in it?",
    ]},

    {"type": "para", "text":
     "If any check fails, the question never reaches the database at all. The robot just "
     "replies that it can't do that — politely, and without pretending to have tried."},

    {"type": "callout", "style": "kid", "label": "Kid's Eye View", "text":
     "It's like airport security. The scanner doesn't sit there and *think* about whether "
     "your bag looks trustworthy today — it runs the exact same scan on everyone, every "
     "time. That's actually what makes it safe: no favorites, no bad days, no talking "
     "your way past it."},

    {"type": "callout", "style": "business", "label": "Business Lens", "text":
     "A rule-based control is auditable in a way an AI \"promise\" is not — you can point "
     "to the code, write a test for every rule, and prove it holds 100% of the time. "
     "That's the difference between a control you can put in front of a compliance "
     "reviewer and one you can only hope works. In this project it's called "
     "\"defense-in-depth\": even though the AI is *also* told to only write safe queries, "
     "the deterministic Guard is what actually enforces it."},

    {"type": "pagebreak"},
    {"type": "heading", "level": 1, "text": "Chapter 5 — When Things Go Wrong"},

    {"type": "para", "text":
     "Sometimes the Writer's first attempt at a query is a little off — maybe it uses a "
     "feature the database doesn't actually support. Rather than giving up immediately, "
     "the robot tries a small, bounded recovery: it takes the *exact* error message the "
     "database gave back, hands it to the Writer along with the original question, and "
     "asks for a corrected attempt. This can happen up to twice before the robot gives up "
     "honestly and says so."},

    {"type": "callout", "style": "note", "label": "A Real Example", "text":
     "One database feature (putting a \"top N\" limit inside a certain kind of "
     "sub-question) simply isn't supported by MySQL, the database this project uses. The "
     "first attempt failed with a clear error. That error was fed straight back to the "
     "Writer, which rewrote the query a different way — and it worked on the second try. "
     "No human had to step in while it was running; the system healed itself using the "
     "database's own error message."},

    {"type": "callout", "style": "business", "label": "Business Lens", "text":
     "This bounded retry (capped at two attempts, always) is what makes the system "
     "resilient without becoming unpredictable. A system that retries *forever* can hang "
     "or loop up costs; a system with zero retries fails on every small hiccup. Capping "
     "it, and failing honestly afterward, is a deliberately small, cheap failure mode."},

    {"type": "pagebreak"},
    {"type": "heading", "level": 1, "text": "Chapter 6 — New Words You'll Hear"},

    {"type": "para", "text":
     "A short glossary, in plain language, for the vocabulary that comes up when talking "
     "about this project."},

    {"type": "glossary", "items": [
        ("AI / LLM (\"Large Language Model\")",
         "A computer program trained on enormous amounts of text, so it can read a "
         "question and write a reasonable-sounding response. It's very good at language, "
         "but it doesn't actually \"know\" facts the way a database does — which is "
         "exactly why this project never lets it answer from memory alone."),
        ("Prompt",
         "The instructions and information you hand the AI right before asking it to "
         "respond — in this project, that includes a description of the database and "
         "your recent conversation."),
        ("Temperature",
         "A setting that controls how \"creative\" vs. \"predictable\" the AI's answers "
         "are. This project uses the lowest setting (0), because for writing database "
         "queries, boring and consistent beats creative."),
        ("SQL",
         "\"Structured Query Language\" — the standard language used to ask a database "
         "questions like \"how many\" or \"what's the total.\" SELECT is the SQL word "
         "for \"just show me,\" as opposed to words that change data."),
        ("Database / Table",
         "A very organized set of spreadsheets (called tables) that a computer can search "
         "through instantly. This project's database has five tables: stores, products, "
         "customers, sales transactions, and returns."),
        ("Schema",
         "A description of what each table contains and how the tables relate to each "
         "other — like a table of contents for the database, so the Writer knows what "
         "questions are even answerable."),
        ("API Key",
         "A private password-like code that proves you're allowed to use an AI service. "
         "It's kept in a hidden settings file and is never shared, printed, or saved "
         "anywhere public — treat it exactly like a bank PIN."),
        ("Agent / LangGraph",
         "\"Agent\" is the general term for a program that uses AI to take a sequence of "
         "actions toward a goal, instead of just answering one question. LangGraph is the "
         "specific tool used here to wire the Writer, Guard, Runner, and Narrator "
         "together into that fixed relay-race order."),
    ]},

    {"type": "pagebreak"},
    {"type": "heading", "level": 1, "text": "Chapter 7 — The Full Technical Map"},

    {"type": "para", "text":
     "For anyone who wants the fuller picture — the exact numbers, the file names, the "
     "precise rules — here's the one-page reference version of everything in this book. "
     "You don't need to memorize it. Just know it's here to come back to."},

    {"type": "image", "path": "infographic_pipeline.png",
     "caption": "The full technical reference poster for this project's pipeline.",
     "width_in": 5.9},

    {"type": "pagebreak"},
    {"type": "heading", "level": 1, "text": "Chapter 8 — Build It Yourself: A Weekend Project"},

    {"type": "para", "text":
     "This whole robot runs on Dad's laptop — no special hardware, and the AI service it "
     "uses is free. Here's how to bring it up from nothing and have your own conversation "
     "with it. Budget about 30–45 minutes the first time, with a grown-up nearby to help "
     "read error messages."},

    {"type": "callout", "style": "kid", "label": "Before You Start", "text":
     "This is exactly what real software engineers do: follow a checklist, one step at a "
     "time, and don't panic if something doesn't work on the first try. It almost never "
     "does, for anyone."},

    {"type": "heading", "level": 2, "text": "Step 1 — Gather the ingredients"},
    {"type": "para", "text":
     "Three things need to be installed once: Python (the programming language the robot "
     "is written in), uv (a tool that installs all the smaller pieces the project needs), "
     "and MySQL (the database itself)."},

    {"type": "heading", "level": 2, "text": "Step 2 — Get a library card for the AI"},
    {"type": "para", "text":
     "Sign up for a free account at Groq (the company providing the AI \"brain\") and "
     "copy your personal API key — a long code that's your private ticket to use it."},

    {"type": "heading", "level": 2, "text": "Step 3 — Give the robot its secrets, privately"},
    {"type": "para", "text":
     "Copy the file named .env.example to a new file named .env, and paste in your API "
     "key and your database password. This file is like a locked diary: the robot reads "
     "it to log in, but it's never shown to anyone else and never saved on the internet."},

    {"type": "heading", "level": 2, "text": "Step 4 — Fill the pretend store with data"},
    {"type": "para", "text":
     "Run one command (uv run scripts/load_data.py) and the robot will build its five "
     "tables and fill them with a year's worth of made-up — but realistic — store sales, "
     "so there's something real to ask about."},

    {"type": "heading", "level": 2, "text": "Step 5 — Say hello"},
    {"type": "para", "text":
     "Run uv run app.py, and you'll get a prompt where you can just start typing "
     "questions in plain English. Try Chapter 9 for ideas."},

    {"type": "callout", "style": "kid", "label": "Prefer a Web Page?", "text":
     "There's also a browser version, if typing into a plain black window isn't your "
     "thing. Run uv run streamlit run app_streamlit.py instead, and it opens a proper "
     "chat page — the same robot, the same rules, just with a friendlier face and a "
     "table for the numbers."},

    {"type": "callout", "style": "note", "label": "If Something Breaks", "text":
     "Copy the exact red error message and read the last line first — it almost always "
     "says what went wrong in plain words (\"file not found,\" \"access denied,\" "
     "\"connection refused\"). Every programmer, including the one who built this, sees "
     "these messages daily. They're not a sign anything is broken forever — just a clue "
     "to fix."},

    {"type": "pagebreak"},
    {"type": "heading", "level": 1, "text": "Chapter 9 — Questions to Try Asking"},

    {"type": "heading", "level": 2, "text": "For the curious 10-year-old"},
    {"type": "bullets", "items": [
        "How many stores do we have?",
        "What's the most popular way people pay — cash, card, or UPI?",
        "Which product category sells the most?",
        "How many products do we sell in total?",
        "What's the most expensive product in the store?",
    ]},

    {"type": "heading", "level": 2, "text": "For the business mind"},
    {"type": "bullets", "items": [
        "What are our top 5 products by revenue?",
        "Which store has the highest return rate?",
        "How much revenue came through UPI versus credit card?",
        "Which city's stores are generating the most sales?",
        "What percentage of revenue is lost to returns?",
    ]},

    {"type": "callout", "style": "note", "label": "Try This Too", "text":
     "Ask it something the database genuinely can't answer — like \"what will the weather "
     "be tomorrow?\" — and watch it politely decline instead of making something up. Then "
     "try asking it to \"delete all the returns\" and watch the Guard step in. Both are "
     "working exactly as designed."},

    {"type": "pagebreak"},
    {"type": "heading", "level": 1, "text": "Chapter 10 — Quiz Time!"},
    {"type": "para", "text":
     "No peeking at the answer key until you've had a guess. Play together — some of "
     "these are just as fun for grown-ups."},

    {"type": "quiz", "items": [
        {"q": "Which team member checks whether a question is safe before it ever "
              "reaches the database?",
         "options": ["The Writer", "The Guard", "The Runner", "The Narrator"],
         "answer": "The Guard"},
        {"q": "True or False: The Narrator is allowed to make up a number if it isn't "
              "sure of the real answer.",
         "options": ["True", "False"],
         "answer": "False — it must only use numbers that actually came back from the "
                   "database."},
        {"q": "Put these in the correct order: Runner fetches · Guard checks · Narrator "
              "explains · Writer drafts.",
         "options": None,
         "answer": "Writer drafts → Guard checks → Runner fetches → "
                   "Narrator explains"},
        {"q": "If a question's SQL contains the word DROP, what happens?",
         "options": ["It runs anyway, carefully",
                     "It gets blocked and the robot politely declines",
                     "It asks a grown-up for permission first"],
         "answer": "It gets blocked and the robot politely declines"},
        {"q": "Discuss: why use a fixed checklist for safety instead of just asking the "
              "AI to \"please be careful\"?",
         "options": None,
         "answer": "Open discussion — a checklist runs the same way every time and can "
                   "be proven correct; an AI's promise can occasionally be misunderstood "
                   "or tricked."},
        {"q": "Bonus for the business mind: name one reason a company would insist the "
              "safety check be deterministic code rather than another AI's judgment call.",
         "options": None,
         "answer": "Open discussion — auditability: you can test and prove a rule holds "
                   "100% of the time, which you can't do with an AI's judgment."},
    ]},

    {"type": "pagebreak"},
    {"type": "heading", "level": 1, "text": "Chapter 11 — Where to Go Further"},

    {"type": "para", "text":
     "Everything in this book has a \"real\" version in the actual project folder, for "
     "whenever you're ready to look closer:"},

    {"type": "bullets", "items": [
        "README.md — the full setup and architecture notes",
        "ai_usage.md — every bug that was caught during human review, and how it was "
        "fixed",
        "rubric.md — how the finished project was evaluated against its original brief",
    ]},

    {"type": "para", "text":
     "None of this required being a professional programmer to understand at the level "
     "this book covers — just the willingness to ask \"but why?\" one layer at a time. "
     "That's the whole skill. Go ask the robot something."},
]
