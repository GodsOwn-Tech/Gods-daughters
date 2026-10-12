"""
seed.py — populates Bible studies (with sessions), Mood Help articles,
Mood Help comfort emojis + verses, the verse-of-the-day list, and
affirmations. Run with: python seed.py
This is content you (the admin) publish, as opposed to user-submitted
prayer wall / gist posts.
"""
import uuid
from database import get_connection, init_db


def new_id():
    return uuid.uuid4().hex[:16]


init_db()
conn = get_connection()
c = conn.cursor()

# Clear existing seeded content so this script can be re-run safely.
c.execute("DELETE FROM bible_studies")
c.execute("DELETE FROM study_sessions")
c.execute("DELETE FROM mood_help")
c.execute("DELETE FROM mood_emojis")
c.execute("DELETE FROM votd_verses")
c.execute("DELETE FROM affirmations")

# ---------------------------------------------------------------------
# Bible studies + their sessions.
# Scripture text itself is never stored here — it's looked up live from
# bible-api.com (public domain WEB translation) using the scripture_ref
# below, via GET /api/scripture?ref=...
# ---------------------------------------------------------------------

ruth_id = new_id()
fruit_id = new_id()
lament_id = new_id()
purity_id = new_id()
relationships_id = new_id()

bible_studies = [
    (ruth_id, 1, "The Book of Ruth", "Loyalty, loss, and quiet faithfulness", 4),
    (fruit_id, 2, "Fruit of the Spirit", "What actually grows when you stay rooted", 6),
    (lament_id, 3, "Psalms of Lament", "Bringing God your real feelings, not just the nice ones", 5),
    (purity_id, 4, "Sexual Purity", "Your body, your worth, and waiting well", 6),
    (relationships_id, 5, "Relationships", "Friendship, family, dating, and who you let close", 6),
]
c.executemany(
    "INSERT INTO bible_studies (id, week, title, description, sessions) VALUES (?, ?, ?, ?, ?)",
    bible_studies,
)

study_sessions = [
    # --- The Book of Ruth ---
    (new_id(), ruth_id, 1, "A Famine and a Faithful Choice", "Ruth 1:1-18",
     "What does Ruth give up to stay with Naomi, and what does that cost her?\n"
     "Have you ever had to choose loyalty to someone even when it was hard? What happened?\n"
     "What does this passage say about the kind of love that stays?"),
    (new_id(), ruth_id, 2, "Gleaning in Boaz's Field", "Ruth 2:1-13",
     "How does Boaz notice and respond to Ruth's situation?\n"
     "Where have you experienced unexpected kindness during a hard season?\n"
     "What does it look like to work faithfully even in uncertainty?"),
    (new_id(), ruth_id, 3, "A Bold Request", "Ruth 3:1-13",
     "What risk does Ruth take in this chapter, and why?\n"
     "What's something you've had to be vulnerable about in order to move forward?\n"
     "How does Boaz's response reflect character, not just attraction?"),
    (new_id(), ruth_id, 4, "Redemption and a New Beginning", "Ruth 4:1-17",
     "How does this chapter show God working through ordinary, even messy, circumstances?\n"
     "What does Ruth's story tell you about how God redeems difficult chapters of life?\n"
     "Where in your own story might God be writing redemption you can't see yet?"),

    # --- Fruit of the Spirit (Galatians 5:22-23) ---
    (new_id(), fruit_id, 1, "Love & Joy", "Galatians 5:22-23",
     "How does Paul describe the fruit of the Spirit differently from a list of rules?\n"
     "What's the difference between joy and just feeling happy?\n"
     "Where do you most need love or joy to grow right now?"),
    (new_id(), fruit_id, 2, "Peace & Patience", "Philippians 4:6-7",
     "What does this passage say to do with anxiety, specifically?\n"
     "What's one situation right now that's testing your patience?\n"
     "What would it look like to bring that situation to God instead of just white-knuckling through it?"),
    (new_id(), fruit_id, 3, "Kindness & Goodness", "Ephesians 4:32",
     "What's the connection this verse draws between being forgiven and being kind to others?\n"
     "Who's someone that's been genuinely kind to you recently?\n"
     "Is there someone you're struggling to extend kindness to right now?"),
    (new_id(), fruit_id, 4, "Faithfulness", "Lamentations 3:22-23",
     "What does it mean that these mercies are 'new every morning'?\n"
     "What helps you stay faithful in seasons when you don't feel like it?\n"
     "How is God's faithfulness to you different from your faithfulness to Him?"),
    (new_id(), fruit_id, 5, "Gentleness", "Philippians 4:5",
     "What does gentleness look like in a world that often rewards harshness?\n"
     "Is gentleness something you associate with strength or weakness? Why?\n"
     "Who models gentleness well in your life?"),
    (new_id(), fruit_id, 6, "Self-Control", "1 Corinthians 9:24-27",
     "What metaphor does Paul use here, and why do you think he chose it?\n"
     "What's an area where self-control feels especially hard right now?\n"
     "What's one small, doable step toward more self-control this week?"),

    # --- Psalms of Lament ---
    (new_id(), lament_id, 1, "How Long, O Lord?", "Psalm 13",
     "What does David actually say to God in this psalm — and does it surprise you that this is in the Bible?\n"
     "Have you ever prayed something this honest? What stopped you, if not?\n"
     "Notice the shift by the end of the psalm. What changes, and what doesn't?"),
    (new_id(), lament_id, 2, "Why Are You Downcast, O My Soul?", "Psalm 42",
     "What images does the psalmist use to describe longing for God?\n"
     "The psalmist talks to his own soul in this passage. What would you say to yours right now?\n"
     "What's one thing that has helped you remember God's presence in a dry season?"),
    (new_id(), lament_id, 3, "My God, My God, Why Have You Forsaken Me?", "Psalm 22",
     "This psalm is quoted by Jesus on the cross. What does that tell you about the place of lament in faith?\n"
     "What's the difference between despair and lament, based on this psalm?\n"
     "Where do you need permission to be this honest with God?"),
    (new_id(), lament_id, 4, "Sitting in the Dark", "Psalm 88",
     "This psalm doesn't end with a resolved, hopeful turn like most laments. What do you make of that?\n"
     "Is it uncomfortable to read a prayer that doesn't wrap up neatly? Why might that still be Scripture?\n"
     "Have you ever had to just sit in a hard season without a tidy resolution?"),
    (new_id(), lament_id, 5, "Turning Mourning into Dancing", "Psalm 30",
     "How does the psalmist describe the shift from grief to joy?\n"
     "What's a hard season you've come through, and what changed?\n"
     "What would it look like to thank God today for something you couldn't see a reason for yet?"),

    # --- Sexual Purity ---
    (new_id(), purity_id, 1, "Made and Loved", "1 Corinthians 6:19-20",
     "What does it mean that your body is described as a temple?\n"
     "How does that change the way you think about worth — yours and other people's?\n"
     "Where do you find it hardest to believe your body and choices have dignity?"),
    (new_id(), purity_id, 2, "What the World Says vs. What God Says", "Romans 12:2",
     "What messages about sex and relationships do you hear most often from media or friends?\n"
     "How does this verse describe the process of thinking differently — is it instant or ongoing?\n"
     "What's one belief you'd like God to help you 'renew' in this area?"),
    (new_id(), purity_id, 3, "Guarding Your Heart", "Proverbs 4:23",
     "What does it look like practically to 'guard' something you value?\n"
     "What inputs (shows, conversations, relationships) tend to shape your heart the most right now?\n"
     "Is there a boundary you've been avoiding setting? What's holding you back?"),
    (new_id(), purity_id, 4, "Grace for the Past", "Psalm 51:10",
     "This psalm is a prayer of someone who messed up badly. What does it ask God for?\n"
     "Is there shame you're still carrying that you haven't brought to God?\n"
     "What's the difference between conviction and shame, based on this psalm?"),
    (new_id(), purity_id, 5, "Purity in Dating", "1 Thessalonians 4:3-7",
     "What reason does this passage give for pursuing purity — fear, or something else?\n"
     "What boundaries have you found helpful (or wish you'd had) in a relationship?\n"
     "How can purity be something you pursue together with someone, not just alone?"),
    (new_id(), purity_id, 6, "Waiting Isn't Wasted", "1 Timothy 4:12",
     "What does it look like to 'set an example' at your age, according to this verse?\n"
     "What's hard about waiting when it feels like everyone else isn't?\n"
     "Who's someone whose patience or integrity in this area has quietly influenced you?"),

    # --- Relationships ---
    (new_id(), relationships_id, 1, "What Real Friendship Looks Like", "Proverbs 17:17",
     "What's the difference between a friend and someone who's just around?\n"
     "Who in your life loves you 'at all times,' including the hard seasons?\n"
     "What kind of friend have you been able to be for someone else lately?"),
    (new_id(), relationships_id, 2, "Iron Sharpens Iron", "Proverbs 27:17",
     "What does it mean for a friendship to 'sharpen' you rather than just entertain you?\n"
     "Do your closest friendships challenge you to grow, or mostly just feel comfortable?\n"
     "Who could you be a sharpening influence for, rather than just a mirror?"),
    (new_id(), relationships_id, 3, "Unequally Yoked: What It Means", "2 Corinthians 6:14",
     "This verse uses a farming image — two animals yoked together pulling one direction. What's the point being made about partnership?\n"
     "What does 'unequally yoked' mean to you in the context of dating or close partnership?\n"
     "Why might shared values matter more long-term than shared chemistry?"),
    (new_id(), relationships_id, 4, "Choosing Wisely in Dating", "Amos 3:3",
     "This verse asks a simple question about walking together without agreeing on direction. How does that apply to relationships?\n"
     "What values or life direction matter most to you in someone you'd date long-term?\n"
     "What's a green flag and a red flag you've learned to notice?"),
    (new_id(), relationships_id, 5, "Loving Difficult Family", "Ephesians 4:2-3",
     "What does this verse ask of us, even when relationships are hard?\n"
     "Who in your family is hardest to love well right now, and why?\n"
     "What would it look like to honor them without losing yourself?"),
    (new_id(), relationships_id, 6, "Letting Go of Toxic Ties", "Proverbs 13:20",
     "What does this verse say about the influence of who we spend time with?\n"
     "Is there a friendship right now that's shaping you in a direction you don't want to go?\n"
     "What would it look like to lovingly create distance, rather than just cutting someone off coldly?"),
]
c.executemany(
    "INSERT INTO study_sessions (id, study_id, session_number, title, scripture_ref, questions) VALUES (?, ?, ?, ?, ?, ?)",
    study_sessions,
)

mood_help = [
    (new_id(), "anxiety", "When your mind won't stop racing at night",
     "A practical, prayerful way to unwind an anxious spiral before bed."),
    (new_id(), "relationships", "Boundaries are not unloving",
     "What Scripture actually says about protecting your peace."),
    (new_id(), "identity", "Who you are before you do anything",
     "Untangling worth from performance."),
    (new_id(), "doubt", "It's okay to ask hard questions",
     "Doubt isn't the enemy of faith — indifference is."),
]
c.executemany(
    "INSERT INTO mood_help (id, struggle, title, excerpt) VALUES (?, ?, ?, ?)",
    mood_help,
)

# ---------------------------------------------------------------------
# Tap-an-emoji comfort feature. Each emoji has a few short encouraging
# statements (frontend shows a random one) and a few scripture references
# (frontend shows all as tappable chips).
# ---------------------------------------------------------------------

mood_emojis = [
    (new_id(), "😠", "Angry",
     "It's okay to feel angry — even Jesus flipped tables. What matters is what you do next with it.\n"
     "Anger often points to something you care about being hurt. Take a breath before you respond to anything.\n"
     "\"Be angry, and do not sin\" — Ephesians 4:26 reminds us the feeling itself isn't the problem.",
     "James 1:19-20\nEphesians 4:26\nProverbs 15:1"),
    (new_id(), "😢", "Sad",
     "God is close to the brokenhearted (Psalm 34:18). You don't have to perform okay-ness right now.\n"
     "Sadness isn't a lack of faith. Even Jesus wept. Let yourself feel this.\n"
     "This feeling is real, but it isn't the whole story of your life. Give yourself permission to grieve without rushing it.",
     "Psalm 34:18\nMatthew 5:4\nPsalm 147:3"),
    (new_id(), "😰", "Anxious",
     "\"Cast all your anxiety on Him because He cares for you\" — 1 Peter 5:7. That includes this exact worry.\n"
     "Try naming one thing you can control right now, and let the rest wait.\n"
     "Anxiety can feel like your body sounding an alarm even when you're safe. A few slow breaths can help your body catch up with the truth.",
     "Philippians 4:6-7\n1 Peter 5:7\nMatthew 6:34"),
    (new_id(), "😔", "Lonely",
     "Loneliness is one of the hardest feelings to sit with — you're not weak for feeling it.\n"
     "God promises He will never leave you or forsake you (Deuteronomy 31:6), even when people feel far away.\n"
     "Consider reaching out to one person today, even just to say hi. Connection often starts small.",
     "Deuteronomy 31:6\nPsalm 68:6\nHebrews 13:5"),
    (new_id(), "😩", "Overwhelmed",
     "You don't have to carry everything today. Pick one small thing and start there.\n"
     "\"Come to me, all who are weary and burdened, and I will give you rest\" — Matthew 11:28.\n"
     "It's okay to say no to something so you have room to breathe.",
     "Matthew 11:28-30\nPsalm 61:2\nIsaiah 41:10"),
    (new_id(), "😕", "Doubtful",
     "Doubt isn't the opposite of faith — indifference is. Asking questions means you still care.\n"
     "Some of the most faithful people in Scripture wrestled hard with God (see Jacob, Job, even John the Baptist).\n"
     "It's okay not to have this figured out today. Faith can hold your questions.",
     "Mark 9:24\nJames 1:5-6\nPsalm 73:26"),
    (new_id(), "😞", "Discouraged",
     "\"Weeping may stay for the night, but joy comes in the morning\" — Psalm 30:5. This feeling is not permanent.\n"
     "Discouragement often lies about how things will always be. Try to name one thing that's still good today.\n"
     "You've made it through hard days before. That matters more than it feels like right now.",
     "Psalm 30:5\nJoshua 1:9\nIsaiah 40:31"),
    (new_id(), "😊", "Grateful",
     "Savor this — noticing good things is its own quiet act of faith.\n"
     "Consider writing this feeling down somewhere so you can find it again on a harder day.\n"
     "\"Give thanks in all circumstances\" doesn't mean everything is good — it means gratitude can coexist with hard seasons too.",
     "1 Thessalonians 5:18\nPsalm 107:1\nColossians 3:15"),
]
c.executemany(
    "INSERT INTO mood_emojis (id, emoji, label, messages, verses) VALUES (?, ?, ?, ?, ?)",
    mood_emojis,
)

# ---------------------------------------------------------------------
# Verse of the day — which one shows is picked by today's date (see
# main.py), cycling through this list all year.
# ---------------------------------------------------------------------

votd_verses = [
    "Jeremiah 29:11", "Philippians 4:13", "Psalm 46:1", "Isaiah 41:10",
    "Proverbs 3:5-6", "Romans 8:28", "Psalm 23:1", "Matthew 11:28",
    "Joshua 1:9", "Psalm 34:18", "2 Corinthians 12:9", "Psalm 27:1",
    "Philippians 4:6-7", "Romans 15:13", "Psalm 91:1-2", "Isaiah 40:31",
    "Psalm 121:1-2", "John 14:27", "Psalm 46:10", "Lamentations 3:22-23",
    "Zephaniah 3:17", "Psalm 139:14", "1 Peter 5:7", "Psalm 16:11",
    "Nahum 1:7", "Psalm 73:26", "Isaiah 43:2", "Psalm 18:2",
    "Habakkuk 3:19", "Psalm 55:22",
]
c.executemany(
    "INSERT INTO votd_verses (id, reference) VALUES (?, ?)",
    [(new_id(), ref) for ref in votd_verses],
)

# ---------------------------------------------------------------------
# Affirmations — six shown as floating bubbles at the top of Devotionals.
# ---------------------------------------------------------------------

affirmations = [
    "You are fearfully and wonderfully made 💗",
    "God's plans for you are good ✨",
    "You are enough, just as you are today 🌸",
    "You are deeply, unconditionally loved 🕊️",
    "Your story isn't over — keep going 🌱",
    "You carry light wherever you go ☀️",
]
c.executemany(
    "INSERT INTO affirmations (id, text) VALUES (?, ?)",
    [(new_id(), text) for text in affirmations],
)

conn.commit()
conn.close()
print("Seeded bible studies + sessions, mood help articles, mood emojis + verses, verse-of-day list, and affirmations into database.db")
