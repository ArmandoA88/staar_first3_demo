param(
    [string]$SourceWorkbook = "C:\Users\laptop\Desktop\staar_first3_demo\Blooket\blooket_template_copy.xlsx",
    [string]$OutputWorkbook = "C:\Users\laptop\Desktop\staar_first3_demo\Blooket\Grade3_ELAR_STAAR_Blooket_Import.xlsx"
)

$ErrorActionPreference = "Stop"

$outputDirectory = Split-Path -Path $OutputWorkbook -Parent
if (-not (Test-Path -LiteralPath $outputDirectory)) {
    New-Item -ItemType Directory -Path $outputDirectory | Out-Null
}

$questions = @'
[
  {
    "question": "Concept: Use context clues to figure out a word's meaning. Question: In the sentence \"A cactus can survive with little water,\" what does survive mean?",
    "answers": ["dance", "share", "stay alive", "play"],
    "correct": "3",
    "time": 35
  },
  {
    "question": "Concept: Context clues can explain describing words. Question: In the sentence \"The sly fox slipped past the hens,\" what does sly mean?",
    "answers": ["tricky", "sleepy", "noisy", "hungry"],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: Context clues can explain action words. Question: In the sentence \"Kai snatched the hat before the wind blew it away,\" what does snatched mean?",
    "answers": ["grabbed quickly", "lost forever", "washed carefully", "folded neatly"],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: Context clues help readers picture actions. Question: In the sentence \"Mina cradled the puppy in her arms,\" what does cradled mean?",
    "answers": ["held gently", "pushed aside", "called loudly", "covered with mud"],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: Word meaning questions ask what a word means in context. Question: An expert is a person who -",
    "answers": ["is highly skilled", "is willing to help", "enjoys working with machines", "learns only by watching"],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: The suffix -less means without. Question: What does cloudless mean?",
    "answers": ["close", "without clouds", "dark", "scary"],
    "correct": "2",
    "time": 35
  },
  {
    "question": "Concept: The prefix dis- often means not. Question: What does disbelief mean?",
    "answers": ["believing more", "not being able to believe", "helping others believe", "believing again"],
    "correct": "2",
    "time": 35
  },
  {
    "question": "Concept: The suffix -ful means full of. Question: What does joyful mean?",
    "answers": ["full of joy", "without joy", "feeling sleepy", "ready to leave"],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: The prefix pre- means before. Question: What does preview mean?",
    "answers": ["to view again", "to view before", "to view slowly", "to view alone"],
    "correct": "2",
    "time": 35
  },
  {
    "question": "Concept: A synonym has almost the same meaning. Question: Which word is a synonym for floating?",
    "answers": ["drifting", "sinking", "hiding", "crashing"],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: An antonym is the opposite of a word. Question: Which word is an antonym of fancy?",
    "answers": ["sour", "plain", "small", "quick"],
    "correct": "2",
    "time": 35
  },
  {
    "question": "Concept: Synonyms connect familiar words to new words. Question: Which word is a synonym for create?",
    "answers": ["build", "break", "lose", "hide"],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: A synonym matches a word's meaning. Question: Which word is a synonym for special?",
    "answers": ["unique", "busy", "open", "tiny"],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: Some words have more than one meaning. Question: Read this entry: pass 1. ignore 2. move by 3. throw a ball to a teammate 4. complete a class. In the sentence \"The car passed our house,\" which meaning matches passed?",
    "answers": ["Meaning 1", "Meaning 2", "Meaning 3", "Meaning 4"],
    "correct": "2",
    "time": 40
  },
  {
    "question": "Concept: Multiple-meaning words change with context. Question: In the sentence \"Ms. Lee will judge the art contest,\" what does judge mean?",
    "answers": ["to decide", "to run quickly", "to draw a picture", "to borrow something"],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: A folktale is passed down over time and often teaches a lesson. Question: Which idea best shows that a story is a folktale?",
    "answers": ["It teaches a lesson.", "It lists facts in order.", "It explains how to build a kite.", "It gives steps for a recipe."],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: Informational text teaches readers with facts. Question: Which sentence is most likely from informational text?",
    "answers": ["Once the moon smiled at the boy.", "Froghoppers can jump many times their body length.", "The dragon guarded a silver key.", "Maya wished the clouds could talk."],
    "correct": "2",
    "time": 35
  },
  {
    "question": "Concept: The central idea is the main point of a text. Question: Which sentence best states a central idea for an article about school gardens?",
    "answers": ["Gardens have soil, seeds, and tools.", "Students can learn responsibility by caring for plants.", "One student wore green gloves.", "The class planted seeds on Tuesday."],
    "correct": "2",
    "time": 40
  },
  {
    "question": "Concept: A simile compares two things using like or as. Question: Which sentence uses a simile?",
    "answers": ["The bee buzzed past my ear.", "The rabbit was as quick as lightning.", "The wind whispered at night.", "The stars danced above us."],
    "correct": "2",
    "time": 35
  },
  {
    "question": "Concept: Onomatopoeia sounds like the noise it names. Question: Which word is onomatopoeia?",
    "answers": ["giant", "smooth", "buzz", "silent"],
    "correct": "3",
    "time": 35
  },
  {
    "question": "Concept: Authors write to inform, entertain, or persuade. Question: An author writes an article explaining how frogs jump. What is the author's purpose?",
    "answers": ["to inform", "to entertain", "to persuade", "to confuse"],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: Text features help readers understand information quickly. Question: Which text feature would best help a reader compare how far animals jump?",
    "answers": ["a graph", "a dialogue line", "a chapter title", "a character map"],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: Use context clues to understand feelings. Question: In the sentence \"The timid mouse hid behind the box,\" what does timid mean?",
    "answers": ["brave", "shy", "noisy", "hungry"],
    "correct": "2",
    "time": 35
  },
  {
    "question": "Concept: Context clues help readers understand action words. Question: In the sentence \"Nia sprinted to the bus stop,\" what does sprinted mean?",
    "answers": ["walked slowly", "ran fast", "sat down", "looked around"],
    "correct": "2",
    "time": 35
  },
  {
    "question": "Concept: Context clues can reveal size words. Question: In the sentence \"An enormous whale swam past the boat,\" what does enormous mean?",
    "answers": ["very large", "very quiet", "very shiny", "very young"],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: Context clues can reveal feelings. Question: In the sentence \"Lena felt grateful after her friend helped her,\" what does grateful mean?",
    "answers": ["thankful", "angry", "confused", "sleepy"],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: Context clues explain time words. Question: In the sentence \"The ancient castle stood on the hill for hundreds of years,\" what does ancient mean?",
    "answers": ["very old", "very clean", "very loud", "very small"],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: Context clues explain how things feel or break. Question: In the sentence \"Be careful with the fragile glass,\" what does fragile mean?",
    "answers": ["easy to break", "easy to wash", "fun to use", "hard to lift"],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: Context clues reveal physical states. Question: In the sentence \"After the long hike, Mateo was exhausted,\" what does exhausted mean?",
    "answers": ["very tired", "very hungry", "very brave", "very quiet"],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: Context clues show what a person wants to know. Question: In the sentence \"The curious child opened the book to learn more,\" what does curious mean?",
    "answers": ["wanting to know more", "ready to sleep", "easy to please", "hard to find"],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: Context clues help readers understand group actions. Question: In the sentence \"The students gathered by the door,\" what does gathered mean?",
    "answers": ["came together", "ran apart", "fell asleep", "looked up"],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: Context clues help readers understand quick actions. Question: In the sentence \"Owen glanced at the clock before class,\" what does glanced mean?",
    "answers": ["looked quickly", "slept beside", "carried away", "talked about"],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: Context clues explain describing words. Question: In the sentence \"The sturdy table did not wobble,\" what does sturdy mean?",
    "answers": ["strong", "silent", "tiny", "messy"],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: Context clues explain action words. Question: In the sentence \"The rainbow vanished when the rain stopped,\" what does vanished mean?",
    "answers": ["appeared", "disappeared", "shook", "shined"],
    "correct": "2",
    "time": 35
  },
  {
    "question": "Concept: Context clues can show mood. Question: In the sentence \"The cheerful crowd clapped and smiled,\" what does cheerful mean?",
    "answers": ["happy", "angry", "slow", "careful"],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: Context clues help readers understand how someone speaks. Question: In the sentence \"Dad murmured so the baby could sleep,\" what does murmured mean?",
    "answers": ["spoke softly", "laughed loudly", "ran quickly", "waved happily"],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: Context clues explain helpful actions. Question: In the sentence \"Firefighters came to rescue the kitten,\" what does rescue mean?",
    "answers": ["save from danger", "call for dinner", "paint carefully", "move in circles"],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: Context clues explain how people feel about others. Question: In the sentence \"Tia admired the artist's work,\" what does admired mean?",
    "answers": ["looked at with respect", "forgot all about", "pushed away quickly", "hid from quietly"],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: Context clues help readers understand readiness. Question: In the sentence \"The players were eager to begin the game,\" what does eager mean?",
    "answers": ["excited and ready", "too tired to move", "unsure what to do", "upset and worried"],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: Context clues can show what is common. Question: In the sentence \"It was an ordinary day at school,\" what does ordinary mean?",
    "answers": ["plain", "magical", "dangerous", "expensive"],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: Context clues help readers understand noticing. Question: In the sentence \"Mila noticed a bird on the fence,\" what does noticed mean?",
    "answers": ["saw", "borrowed", "built", "dropped"],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: Context clues explain size and shape words. Question: In the sentence \"The narrow path fit only one hiker,\" what does narrow mean?",
    "answers": ["not wide", "full of light", "very rough", "easy to climb"],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: Context clues explain feelings after a problem ends. Question: In the sentence \"Ava felt relieved when she found her lost shoe,\" what does relieved mean?",
    "answers": ["glad a problem ended", "ready for lunch", "angry at a friend", "excited to travel"],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: Context clues explain body feelings. Question: In the sentence \"The baby became drowsy after the car ride,\" what does drowsy mean?",
    "answers": ["sleepy", "thirsty", "playful", "helpful"],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: Context clues help readers understand value words. Question: In the sentence \"Grandma kept the precious photo in a box,\" what does precious mean?",
    "answers": ["very valuable", "very wet", "very bright", "very heavy"],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: Context clues explain speed. Question: In the sentence \"The swift rabbit crossed the field in seconds,\" what does swift mean?",
    "answers": ["fast", "shy", "careless", "smooth"],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: Context clues explain careful behavior. Question: In the sentence \"Be cautious near the slippery rocks,\" what does cautious mean?",
    "answers": ["careful", "careless", "happy", "curious"],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: Context clues explain permission words. Question: In the sentence \"Mom said I may go, so she will permit the trip,\" what does permit mean?",
    "answers": ["allow", "delay", "forget", "measure"],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: Context clues explain confusion. Question: In the sentence \"Jay looked puzzled by the riddle,\" what does puzzled mean?",
    "answers": ["confused", "cheerful", "brave", "careful"],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: Context clues explain sound words. Question: In the sentence \"The shout echoed through the canyon,\" what does echoed mean?",
    "answers": ["made a repeated sound", "faded away softly", "stopped all at once", "sang a happy song"],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: The suffix -less means without. Question: What does careless mean?",
    "answers": ["without care", "full of care", "care before", "not able to care"],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: The suffix -less means without. Question: What does powerless mean?",
    "answers": ["full of power", "without power", "before power", "power again"],
    "correct": "2",
    "time": 35
  },
  {
    "question": "Concept: The suffix -y can mean full of. Question: What does windy mean?",
    "answers": ["without wind", "before wind", "full of wind", "moving like wind"],
    "correct": "3",
    "time": 35
  },
  {
    "question": "Concept: The suffix -y can mean full of. Question: What does snowy mean?",
    "answers": ["full of snow", "without snow", "snow again", "before snow"],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: The suffix -y can mean full of. Question: What does rocky mean?",
    "answers": ["full of rocks", "without rocks", "before rocks", "under rocks"],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: The suffix -ness names a state or condition. Question: What does darkness mean?",
    "answers": ["the state of being dark", "full of dark", "before dark", "not dark"],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: The suffix -ness names a state or condition. Question: What does kindness mean?",
    "answers": ["the state of being kind", "not kind", "full of kinds", "before kind"],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: The suffix -ness names a state or condition. Question: What does sickness mean?",
    "answers": ["the state of being sick", "full of medicine", "not sick", "before sickness"],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: The prefix dis- often means not. Question: What does dishonest mean?",
    "answers": ["not honest", "very honest", "honest again", "honest before"],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: The prefix dis- often means not. Question: What does disagree mean?",
    "answers": ["agree strongly", "not agree", "agree later", "agree before"],
    "correct": "2",
    "time": 35
  },
  {
    "question": "Concept: The prefix in- often means not. Question: What does inactive mean?",
    "answers": ["not active", "very active", "active again", "active before"],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: The prefix in- often means not. Question: What does invisible mean?",
    "answers": ["very visible", "not visible", "easy to see", "seen before"],
    "correct": "2",
    "time": 35
  },
  {
    "question": "Concept: The prefix non- means not. Question: What does nonfiction mean?",
    "answers": ["not fiction", "full of fiction", "fiction again", "before fiction"],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: The prefix non- means not. Question: What does nonstop mean?",
    "answers": ["before stopping", "without stopping", "stopping again", "able to stop"],
    "correct": "2",
    "time": 35
  },
  {
    "question": "Concept: The prefix pre- means before. Question: What does preview mean?",
    "answers": ["to view before", "to view after", "to view without", "to view slowly"],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: The prefix pre- means before. Question: What does preheat mean?",
    "answers": ["to heat after", "to heat without", "to heat before", "to heat again"],
    "correct": "3",
    "time": 35
  },
  {
    "question": "Concept: The prefix im- often means not. Question: What does impossible mean?",
    "answers": ["not possible", "very possible", "possible before", "possible again"],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: The suffix -ful means full of. Question: What does hopeful mean?",
    "answers": ["without hope", "before hope", "full of hope", "hope again"],
    "correct": "3",
    "time": 35
  },
  {
    "question": "Concept: The suffix -y can mean full of. Question: What does rainy mean?",
    "answers": ["full of rain", "without rain", "before rain", "like rain later"],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: The suffix -less means without. Question: What does fearless mean?",
    "answers": ["full of fear", "without fear", "fear before", "fear again"],
    "correct": "2",
    "time": 35
  },
  {
    "question": "Concept: A synonym has almost the same meaning. Question: Which word is a synonym for rapid?",
    "answers": ["quick", "sleepy", "careful", "silent"],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: An antonym is the opposite of a word. Question: Which word is an antonym of enormous?",
    "answers": ["giant", "huge", "tiny", "wide"],
    "correct": "3",
    "time": 35
  },
  {
    "question": "Concept: A synonym has almost the same meaning. Question: Which word is a synonym for silent?",
    "answers": ["loud", "quiet", "rough", "bright"],
    "correct": "2",
    "time": 35
  },
  {
    "question": "Concept: An antonym is the opposite of a word. Question: Which word is an antonym of empty?",
    "answers": ["blank", "full", "open", "hollow"],
    "correct": "2",
    "time": 35
  },
  {
    "question": "Concept: A synonym has almost the same meaning. Question: Which word is a synonym for begin?",
    "answers": ["finish", "start", "rest", "hide"],
    "correct": "2",
    "time": 35
  },
  {
    "question": "Concept: An antonym is the opposite of a word. Question: Which word is an antonym of early?",
    "answers": ["fast", "late", "small", "ready"],
    "correct": "2",
    "time": 35
  },
  {
    "question": "Concept: A synonym has almost the same meaning. Question: Which word is a synonym for choose?",
    "answers": ["drop", "pick", "climb", "measure"],
    "correct": "2",
    "time": 35
  },
  {
    "question": "Concept: An antonym is the opposite of a word. Question: Which word is an antonym of ancient?",
    "answers": ["old", "broken", "new", "hidden"],
    "correct": "3",
    "time": 35
  },
  {
    "question": "Concept: A synonym has almost the same meaning. Question: Which word is a synonym for repair?",
    "answers": ["carry", "fix", "wrap", "point"],
    "correct": "2",
    "time": 35
  },
  {
    "question": "Concept: An antonym is the opposite of a word. Question: Which word is an antonym of rough?",
    "answers": ["sharp", "smooth", "dusty", "plain"],
    "correct": "2",
    "time": 35
  },
  {
    "question": "Concept: A synonym has almost the same meaning. Question: Which word is a synonym for tiny?",
    "answers": ["small", "heavy", "noisy", "wild"],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: An antonym is the opposite of a word. Question: Which word is an antonym of noisy?",
    "answers": ["quiet", "crowded", "bright", "muddy"],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: A synonym has almost the same meaning. Question: Which word is a synonym for glad?",
    "answers": ["happy", "plain", "tired", "sharp"],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: An antonym is the opposite of a word. Question: Which word is an antonym of safe?",
    "answers": ["quiet", "dangerous", "simple", "calm"],
    "correct": "2",
    "time": 35
  },
  {
    "question": "Concept: A synonym has almost the same meaning. Question: Which word is a synonym for purchase?",
    "answers": ["buy", "lose", "paint", "hide"],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: An antonym is the opposite of a word. Question: Which word is an antonym of above?",
    "answers": ["through", "behind", "below", "near"],
    "correct": "3",
    "time": 35
  },
  {
    "question": "Concept: A synonym has almost the same meaning. Question: Which word is a synonym for clever?",
    "answers": ["smart", "slow", "silent", "plain"],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: An antonym is the opposite of a word. Question: Which word is an antonym of lazy?",
    "answers": ["sleepy", "active", "shy", "curious"],
    "correct": "2",
    "time": 35
  },
  {
    "question": "Concept: A synonym has almost the same meaning. Question: Which word is a synonym for reply?",
    "answers": ["question", "answer", "window", "picture"],
    "correct": "2",
    "time": 35
  },
  {
    "question": "Concept: An antonym is the opposite of a word. Question: Which word is an antonym of strong?",
    "answers": ["solid", "brave", "weak", "sturdy"],
    "correct": "3",
    "time": 35
  },
  {
    "question": "Concept: Some words have more than one meaning. Question: In the sentence \"They sat on the bank of the river,\" what does bank mean?",
    "answers": ["a place for money", "the edge of land by water", "a row of chairs", "a pile of snow"],
    "correct": "2",
    "time": 40
  },
  {
    "question": "Concept: Some words have more than one meaning. Question: In the sentence \"The bark on the tree felt rough,\" what does bark mean?",
    "answers": ["the sound a dog makes", "the outer covering of a tree", "a quick jump", "a kind of leaf"],
    "correct": "2",
    "time": 40
  },
  {
    "question": "Concept: Some words have more than one meaning. Question: In the sentence \"This backpack is light,\" what does light mean?",
    "answers": ["not heavy", "a lamp", "bright fire", "a flash in the sky"],
    "correct": "1",
    "time": 40
  },
  {
    "question": "Concept: Some words have more than one meaning. Question: In the sentence \"A bat flew out of the cave,\" what does bat mean?",
    "answers": ["a flying mammal", "sports equipment", "a small boat", "a kind of hat"],
    "correct": "1",
    "time": 40
  },
  {
    "question": "Concept: Some words have more than one meaning. Question: In the sentence \"Flowers bloom in spring,\" what does spring mean?",
    "answers": ["a metal coil", "a quick jump", "a season", "a deep well"],
    "correct": "3",
    "time": 40
  },
  {
    "question": "Concept: Some words have more than one meaning. Question: In the sentence \"The traffic jam made us late,\" what does jam mean?",
    "answers": ["fruit spread", "cars stuck together", "a song", "a sharp tool"],
    "correct": "2",
    "time": 40
  },
  {
    "question": "Concept: Some words have more than one meaning. Question: In the sentence \"What kind of bird is that?\" what does kind mean?",
    "answers": ["nice behavior", "a type", "a small gift", "a loud sound"],
    "correct": "2",
    "time": 40
  },
  {
    "question": "Concept: Some words have more than one meaning. Question: In the sentence \"Watch the turtle cross the path,\" what does watch mean?",
    "answers": ["a timepiece", "to look carefully", "to fix something", "to turn around"],
    "correct": "2",
    "time": 40
  },
  {
    "question": "Concept: Some words have more than one meaning. Question: In the sentence \"We heard the ring of the bell,\" what does ring mean?",
    "answers": ["a piece of jewelry", "a circular mark", "a sound", "a game"],
    "correct": "3",
    "time": 40
  },
  {
    "question": "Concept: Some words have more than one meaning. Question: In the sentence \"The teacher made a fair rule,\" what does fair mean?",
    "answers": ["just", "light-colored", "a carnival", "windy"],
    "correct": "1",
    "time": 40
  },
  {
    "question": "Concept: Some words have more than one meaning. Question: In the sentence \"Be careful not to trip on the rug,\" what does trip mean?",
    "answers": ["a journey", "to stumble", "a kind of shoe", "to clap loudly"],
    "correct": "2",
    "time": 40
  },
  {
    "question": "Concept: Some words have more than one meaning. Question: In the sentence \"These socks match,\" what does match mean?",
    "answers": ["to go together", "a stick for fire", "a sports game", "to smell alike"],
    "correct": "1",
    "time": 40
  },
  {
    "question": "Concept: Some words have more than one meaning. Question: In the sentence \"Duck when the ball comes close!\" what does duck mean?",
    "answers": ["a bird", "to lower your head", "to swim slowly", "to call for help"],
    "correct": "2",
    "time": 40
  },
  {
    "question": "Concept: Some words have more than one meaning. Question: In the sentence \"Please seal the box,\" what does seal mean?",
    "answers": ["an ocean animal", "to close tightly", "to draw a circle", "to carry outside"],
    "correct": "2",
    "time": 40
  },
  {
    "question": "Concept: Some words have more than one meaning. Question: In the sentence \"Mom left a note on the table,\" what does note mean?",
    "answers": ["a short message", "a loud song", "a shiny coin", "a warm blanket"],
    "correct": "1",
    "time": 40
  },
  {
    "question": "Concept: Genre clues help readers identify story types. Question: Which sentence is most likely from realistic fiction?",
    "answers": ["Jordan forgot his backpack on the bus.", "A dragon guarded the cloudy mountain.", "The moon asked the owl for directions.", "A giant pencil wrote its own homework."],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: Genre clues help readers identify fantasy. Question: Which sentence is most likely from fantasy?",
    "answers": ["The class lined up for lunch.", "A dragon guarded the bridge.", "Dad fixed the squeaky door.", "Mina planted beans in the garden."],
    "correct": "2",
    "time": 35
  },
  {
    "question": "Concept: A biography tells the true story of a real person. Question: Which book is most likely a biography?",
    "answers": ["The Life of Jane Goodall", "How to Build a Birdhouse", "The Dragon's Secret Cave", "Poems for Rainy Days"],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: In a drama, characters speak the lines. Question: In a play, who says the words before each line?",
    "answers": ["the characters", "the headings", "the pictures", "the captions"],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: Stage directions tell actors what to do. Question: What is the purpose of stage directions in a play?",
    "answers": ["to tell actors how to move or speak", "to list the page numbers", "to show the glossary words", "to explain the author's life"],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: Poetry often uses short lines and rhythm. Question: Which feature is common in poetry?",
    "answers": ["short lines", "chapter titles only", "recipe steps", "numbered directions"],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: Authors write to inform, entertain, or persuade. Question: An article explains how whales breathe. What is the author's purpose?",
    "answers": ["to inform", "to entertain", "to persuade", "to confuse"],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: Authors sometimes try to persuade readers. Question: A poster says, \"Bring a reusable bottle every day!\" What is the author's purpose?",
    "answers": ["to persuade", "to entertain", "to inform only", "to retell a folktale"],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: Authors write stories to entertain readers. Question: A funny story about a squirrel on roller skates is written mainly -",
    "answers": ["to entertain", "to persuade", "to inform", "to give directions"],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: The central idea is the main point of a text. Question: Which sentence best states a central idea for an article about recycling?",
    "answers": ["Recycling helps reduce trash and reuse materials.", "Some bins are blue and some are green.", "One can rolled across the floor.", "The truck came on Thursday morning."],
    "correct": "1",
    "time": 40
  },
  {
    "question": "Concept: Supporting details help prove the central idea. Question: Which detail best supports the idea that bees help plants grow?",
    "answers": ["Bees carry pollen from flower to flower.", "Bees can be yellow and black.", "Some bees live near gardens.", "A bee has six legs."],
    "correct": "1",
    "time": 40
  },
  {
    "question": "Concept: Captions help explain pictures. Question: What is the purpose of a caption?",
    "answers": ["to explain a picture", "to list the author's hobbies", "to show the answer key", "to start a new chapter"],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: Headings tell what a section is about. Question: What is the purpose of a heading in informational text?",
    "answers": ["to tell what a section is mostly about", "to show who wins the story", "to name each character", "to explain a simile"],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: Diagrams help readers understand parts. Question: Which text feature best shows the parts of a plant?",
    "answers": ["a diagram", "a poem", "a dialogue line", "a chapter title"],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: A simile compares two things using like or as. Question: Which sentence uses a simile?",
    "answers": ["The kitten was as soft as a cloud.", "The kitten purred near the window.", "The kitten chased a string.", "The kitten slept on the rug."],
    "correct": "1",
    "time": 35
  },
  {
    "question": "Concept: Onomatopoeia sounds like the noise it names. Question: Which word is onomatopoeia?",
    "answers": ["silent", "clang", "bright", "gentle"],
    "correct": "2",
    "time": 35
  },
  {
    "question": "Concept: A timeline shows events in time order. Question: Which text feature would best show the order of events in Harriet Tubman's life?",
    "answers": ["a timeline", "a caption", "a pie chart", "a glossary"],
    "correct": "1",
    "time": 35
  }
]
'@ | ConvertFrom-Json

function New-Question {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Question,
        [Parameter(Mandatory = $true)]
        [string]$Answer1,
        [Parameter(Mandatory = $true)]
        [string]$Answer2,
        [Parameter(Mandatory = $true)]
        [string]$Answer3,
        [Parameter(Mandatory = $true)]
        [string]$Answer4,
        [Parameter(Mandatory = $true)]
        [string]$Correct,
        [int]$Time = 35
    )

    [pscustomobject]@{
        question = $Question
        answers  = @($Answer1, $Answer2, $Answer3, $Answer4)
        correct  = $Correct
        time     = $Time
    }
}

function Add-QuestionBlock {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Block
    )

    $lines = $Block -split "\r?\n" | Where-Object { $_.Trim() -ne "" }
    foreach ($line in $lines) {
        $parts = $line -split '\|\|\|'
        if ($parts.Count -ne 7) {
            throw "Invalid question block line: $line"
        }

        $script:questions += New-Question `
            $parts[0].Trim() `
            $parts[1].Trim() `
            $parts[2].Trim() `
            $parts[3].Trim() `
            $parts[4].Trim() `
            $parts[5].Trim() `
            ([int]$parts[6].Trim())
    }
}

$questions += @(
    New-Question "Concept: Theme is the lesson or message of a story. Question: A story shows Maya practicing jump rope every day until she can do new tricks. Which theme best fits the story?" "Practice can help people improve." "Rainy days last forever." "Pets should stay indoors." "People should never ask for help." "1" 40
    New-Question "Concept: Theme is the lesson or message of a story. Question: In a story, two neighbors work together to clean a park and become friends. Which theme best fits the story?" "Teamwork can help people solve problems." "Every park needs taller trees." "Neighbors should stay quiet." "Cleaning is harder than planting." "1" 40
    New-Question "Concept: Theme is different from topic. Question: Which answer is a theme instead of just a topic?" "friendship" "sports" "Being honest builds trust." "school" "3" 40
    New-Question "Concept: Theme tells what a reader can learn from a story. Question: A character admits breaking a lamp and then feels proud for telling the truth. Which theme best fits the story?" "Truthfulness matters." "Lamps cost too much." "Homes need brighter lights." "Mistakes never happen." "1" 40
    New-Question "Concept: Theme tells an important lesson. Question: A runner loses one race but keeps training and wins later. Which theme best fits the story?" "Giving up saves time." "Trying again can lead to success." "Running is easy for everyone." "Winning matters more than effort." "2" 40
    New-Question "Concept: Theme tells what a story teaches. Question: A girl is nervous to sing on stage, but she takes a deep breath and tries. Which theme best fits the story?" "Courage can help people face fears." "Music should always be quiet." "Stages are hard to build." "People sing best when alone." "1" 40
    New-Question "Concept: Theme can be shown by actions and results. Question: A boy rushes through a model airplane, and it falls apart. He rebuilds it slowly and it works. Which theme best fits the story?" "Patience can lead to better results." "Airplanes are hard to paint." "Glue dries too slowly." "Mistakes should be hidden." "1" 40
    New-Question "Concept: Theme tells a lesson readers can use. Question: A class welcomes a new student and helps her learn the routines. Which theme best fits the story?" "Kindness helps others feel included." "Schools need more rules." "New students are always shy." "Classrooms should be larger." "1" 40
    New-Question "Concept: Theme can be shown by actions and responsibility. Question: A child keeps a promise to water a neighbor's plants every day. Which theme best fits the story?" "Responsibility means doing what you said you would do." "Plants need sunlight and water." "Neighbors should travel often." "Summer days feel long." "1" 40
    New-Question "Concept: Theme often comes from what a character learns. Question: A brother laughs at his sister's idea, then sees it work and apologizes. Which theme best fits the story?" "Listening to others can be important." "Brothers should always lead." "Ideas are hard to explain." "Apologies are never needed." "1" 40
    New-Question "Concept: Theme gives a lesson readers can remember. Question: A child shares lunch with a classmate who forgot theirs. Which theme best fits the story?" "Sharing can show care for others." "Lunch should be eaten quickly." "School days need longer breaks." "Food tastes better outdoors." "1" 40
    New-Question "Concept: Theme is the deeper message of a story. Question: A gardener waits many weeks for seeds to sprout and keeps caring for them. Which theme best fits the story?" "Good things can take time." "Gardens need bigger tools." "Seeds grow best in winter." "Plants should be moved often." "1" 40

    New-Question "Concept: Character relationships show how people feel and act toward each other. Question: A girl watches her aunt fix bikes and asks to learn too. Which statement best describes their relationship?" "The girl hopes to learn from her aunt." "The girl is annoyed by her aunt." "The aunt wants to avoid the girl." "The aunt does not trust the girl." "1" 40
    New-Question "Concept: Character relationships can change over time. Question: At first, Eli is upset that his brother tags along. Later, Eli smiles when his brother helps him finish the project. Which statement best describes the change?" "Eli becomes grateful for his brother's help." "Eli stays upset with his brother." "Eli stops speaking to his brother." "Eli forgets about the project." "1" 40
    New-Question "Concept: A character trait is shown by what a person says and does. Question: Nora returns a lost wallet to the office right away. Which trait best describes Nora?" "honest" "careless" "selfish" "forgetful" "1" 35
    New-Question "Concept: A character trait is shown through actions. Question: Sam checks the weather, packs water, and brings a map before a hike. Which trait best describes Sam?" "prepared" "jealous" "bossy" "impatient" "1" 35
    New-Question "Concept: Character relationships can show respect and trust. Question: Ava asks Grandpa to read her writing because she values his advice. Which statement best describes their relationship?" "Ava trusts Grandpa's opinion." "Ava is hiding from Grandpa." "Grandpa is confused by Ava." "Ava is tired of Grandpa." "1" 40
    New-Question "Concept: Readers can describe relationships using evidence from actions. Question: Two friends take turns carrying supplies during a cleanup day. Which statement best describes their relationship?" "They work well as a team." "They are competing to win." "They do not understand each other." "They try to avoid the task." "1" 40
    New-Question "Concept: Character traits can be inferred from behavior. Question: Luis stays after class to erase the board and stack chairs without being asked. Which trait best describes Luis?" "helpful" "greedy" "fearful" "rude" "1" 35
    New-Question "Concept: Character traits can be shown by choices. Question: Mei keeps practicing the same piano piece even when it sounds difficult. Which trait best describes Mei?" "determined" "careless" "lazy" "confused" "1" 35
    New-Question "Concept: Relationships show how characters feel toward one another. Question: Zoe brings soup to her sick neighbor and asks if he needs anything else. Which statement best describes Zoe's attitude?" "Zoe is caring toward her neighbor." "Zoe is angry at her neighbor." "Zoe is afraid of her neighbor." "Zoe is bored by her neighbor." "1" 40
    New-Question "Concept: A character trait can be shown by careful choices. Question: Ben reads all the directions before starting the science activity. Which trait best describes Ben?" "responsible" "reckless" "gloomy" "selfish" "1" 35
    New-Question "Concept: Character relationships can be based on admiration. Question: Tori watches the team captain encourage everyone and begins copying her kind words. Which statement best describes Tori's feelings?" "Tori looks up to the captain." "Tori avoids the captain." "Tori wants to beat the captain." "Tori is confused by the captain." "1" 40
    New-Question "Concept: Readers can tell how characters work together. Question: Omar sketches the poster while Priya writes the facts and both smile at the finished work. Which statement best describes them?" "They cooperate to finish the job." "They argue over every detail." "They try to work alone." "They forget the goal." "1" 40

    New-Question "Concept: Plot includes the problem, events, and solution. Question: In a story, a dog keeps digging up the garden. Which event best shows the conflict?" "The family buys flower seeds." "The dog digs up the new plants each morning." "The children name the dog Pepper." "The rain helps the plants grow." "2" 40
)

$questions += @(
    New-Question "Concept: Plot includes a resolution that solves the problem. Question: A girl cannot reach the library book she wants. Which event best shows the resolution?" "She looks up at the shelf." "She asks a librarian for help and gets the book." "She reads the book title again." "She wonders who borrowed it last." "2" 40
    New-Question "Concept: Sequence means putting events in order. Question: Which event would most likely happen first in a story about baking cookies?" "The cookies cool on a rack." "The batter is mixed in a bowl." "The family eats dessert." "The kitchen is cleaned." "2" 35
    New-Question "Concept: Sequence helps readers follow plot. Question: Which event would most likely happen after a class plants seeds?" "The students harvest vegetables." "The students water the soil." "The students make soup from the vegetables." "The students sell vegetables at a fair." "2" 35
    New-Question "Concept: Conflict is the main problem in a story. Question: Which sentence best shows the conflict in a story about a lost kitten?" "Maya fills a bowl with water." "Maya cannot find the kitten anywhere in the yard." "Maya hears birds in the tree." "Maya sits on the porch steps." "2" 40
    New-Question "Concept: Resolution shows how the problem is solved. Question: Which event best shows the resolution to a story about a broken wagon wheel?" "The children stare at the wheel." "Grandpa repairs the wheel, and the wagon works again." "The wagon squeaks along the path." "The children gather apples near the wagon." "2" 40
    New-Question "Concept: Plot events can lead to later events. Question: Which event most likely causes a character to miss the bus?" "She woke up late after her alarm did not ring." "She packed her backpack the night before." "She waved to a neighbor after school." "She read a book on the couch." "1" 40
    New-Question "Concept: Plot shows how a problem grows. Question: Which event adds to the conflict in a story about a school play?" "The curtain opens at the end." "The main prop breaks on rehearsal day." "The audience claps loudly." "The actors bow together." "2" 40
    New-Question "Concept: Sequence can show how one event affects another. Question: Which event would most likely happen just before a soccer team wins the game?" "The team celebrates with juice." "A player scores the final goal." "The coach plans next week's practice." "Parents drive home from the field." "2" 35
    New-Question "Concept: Conflict often comes from a challenge a character must face. Question: A boy wants to enter a kite contest, but the wind keeps changing. What is the conflict?" "The boy likes bright colors." "The boy must find a way to fly the kite in tricky weather." "The contest gives out blue ribbons." "The crowd cheers for each kite." "2" 40
    New-Question "Concept: Resolution shows what happens after the problem is handled. Question: A class pet escapes from its cage. Which event best shows the resolution?" "The pet hides under a shelf." "The students hear scratching nearby." "The teacher safely returns the pet to the cage." "The class wonders where the pet went." "3" 40
    New-Question "Concept: Plot events happen in a meaningful order. Question: Which event would most likely happen last in a story about building a birdhouse?" "The wood pieces are measured." "The birdhouse is painted and hung outside." "The nails are placed on the table." "The instructions are read aloud." "2" 35
    New-Question "Concept: Conflict can come from not knowing what to do. Question: Which event best shows the conflict in a story about a spelling bee?" "Lena studies her word list." "Lena forgets how to spell the word when it is her turn." "Lena smiles at her teacher." "Lena holds the microphone carefully." "2" 40
    New-Question "Concept: Resolution solves the main story problem. Question: In a story about a torn backpack strap, which event best shows the resolution?" "The strap rips during recess." "The backpack falls to the ground." "A neighbor sews the strap so it can be used again." "The books are heavy inside the bag." "3" 40
    New-Question "Concept: Sequence helps readers see what comes next. Question: A student researches an animal, writes notes, and then makes a poster. Which event most likely comes next?" "The student shares the poster with the class." "The student chooses a topic." "The student visits the library." "The student starts the notes page." "1" 35

    New-Question "Concept: Central idea is the main point of an informational text. Question: Which sentence best states a central idea for an article about recycling at school?" "Recycling helps schools reduce waste and reuse materials." "The blue bin is near the cafeteria." "One student collected cans on Friday." "Some paper is white and some is brown." "1" 40
    New-Question "Concept: Supporting details help prove the central idea. Question: Which detail best supports the idea that exercise helps keep bodies healthy?" "Exercise can make hearts and muscles stronger." "Many people like blue running shoes." "Some parks have benches and fountains." "A soccer ball is round." "1" 40
    New-Question "Concept: Supporting details prove a key idea. Question: Which detail best supports the idea that libraries help communities?" "Libraries lend books and offer reading programs." "Libraries often have brick walls." "Some libraries have two entrances." "Libraries can be near schools." "1" 40
    New-Question "Concept: Central idea tells what most of the text is about. Question: Which sentence best states a central idea for an article about maps?" "Maps help people understand where places are." "Some maps use blue for water." "The classroom globe is round." "One map hangs by the door." "1" 40
    New-Question "Concept: Supporting details connect to the main point. Question: Which detail best supports the idea that bees help plants grow?" "Bees move pollen from flower to flower." "Bees can be black and yellow." "Some bees live in hives." "Bees have six legs." "1" 40
    New-Question "Concept: Central idea is broader than one fact. Question: Which sentence best states a central idea for an article about nocturnal animals?" "Some animals are active at night for food and safety." "Owls have large eyes." "One bat slept in a cave." "The moon shines in the sky." "1" 40
    New-Question "Concept: A supporting detail should directly match the key idea. Question: Which detail best supports the idea that sea turtles need protection?" "Lights near beaches can confuse baby turtles." "Sea turtles have flippers." "Many turtles are green or brown." "Some turtles live a long time." "1" 40
    New-Question "Concept: Central idea tells the main point of a whole section. Question: Which sentence best states a central idea for an article about community helpers?" "Community helpers do different jobs that keep neighborhoods safe and healthy." "A firefighter wears heavy gear." "A librarian shelves books quietly." "A crossing guard stands near the school." "1" 40
    New-Question "Concept: Supporting details help readers understand key ideas. Question: Which detail best supports the idea that rain forests have different layers?" "Some animals live high in the canopy while others live near the ground." "Rain forests receive a lot of rain." "Many rain forests are warm." "Some trees have broad leaves." "1" 40
    New-Question "Concept: Central idea is not just one small fact. Question: Which sentence best states a central idea for an article about compost?" "Compost turns food scraps into material that helps plants grow." "Banana peels are yellow." "A compost bin can be made of wood." "Leaves fall in autumn." "1" 40
    New-Question "Concept: Evidence can support a key idea. Question: Which detail best supports the idea that practice improves skills?" "A swimmer's lap times get faster after weeks of training." "The pool water feels cold in the morning." "The whistle is loud at practice." "Many swimmers wear goggles." "1" 40
)

$questions += @(
    New-Question "Concept: Central idea is what the text mostly teaches. Question: Which sentence best states a central idea for an article about fossils?" "Fossils give clues about plants and animals from long ago." "A fossil can be found in rock." "Some fossils are very small." "Scientists use brushes and tools." "1" 40
    New-Question "Concept: Supporting details should match the main point. Question: Which detail best supports the idea that planets are different from one another?" "Some planets are rocky, while others are made mostly of gas." "People study planets with telescopes." "The night sky looks dark." "Stars can appear tiny." "1" 40
    New-Question "Concept: Central idea explains the big message in nonfiction. Question: Which sentence best states a central idea for an article about bridges?" "Bridges are designed in different ways to help people cross obstacles." "One bridge is painted red." "Cars drive across bridges each day." "Some bridges are older than others." "1" 40
    New-Question "Concept: Readers can identify which details support a main idea. Question: Which detail does NOT support the idea that school gardens teach responsibility?" "Students must remember to water the plants often." "Students take turns pulling weeds from the beds." "Students watch seeds sprout over time." "The school gym floor was polished on Monday." "4" 40

    New-Question "Concept: Author's purpose explains why an author includes information. Question: An article explains how volcanoes form. What is the author's purpose?" "to inform" "to entertain" "to persuade" "to confuse" "1" 35
    New-Question "Concept: Authors include sections for a reason. Question: What is the most likely reason an author includes a section called ""Fast Facts"" in an animal article?" "To present important information quickly" "To tell a funny story" "To describe a character's problem" "To show how to write a poem" "1" 40
    New-Question "Concept: Authors use photographs to support meaning. Question: What is the most likely reason an author includes a photograph of a school garden at the beginning of an article?" "To show what the garden looks like before readers learn about it" "To replace all the written facts" "To introduce a made-up character" "To show the ending of a story" "1" 40
    New-Question "Concept: Author's message can be found through events in a story. Question: A story shows a child trying new foods and discovering she likes them. What message is the author most likely sharing?" "Trying something new can lead to good surprises." "Everyone should eat the same meal." "Cooking is easy for all children." "Food should always look colorful." "1" 40
    New-Question "Concept: Headings support an author's purpose. Question: What is the most likely reason an author includes the heading ""Getting Ready"" in a how-to text?" "To show that the section explains what to do before starting" "To reveal the ending of the text" "To list the author's favorite tools" "To describe a character's feelings" "1" 40
    New-Question "Concept: Print features help authors teach readers. Question: What is the most likely reason an author prints a word in bold in nonfiction text?" "To make an important word stand out" "To show the text is a fantasy story" "To hide a clue from the reader" "To replace a caption" "1" 40
    New-Question "Concept: Authors use diagrams for a purpose. Question: What is the most likely reason an author includes a diagram of the water cycle?" "To help readers understand how the parts work together" "To tell a joke about rain" "To introduce a main character" "To show the author's opinion only" "1" 40
    New-Question "Concept: Authors include quotations to add meaning. Question: What is the most likely reason an author includes a gardener's quote in an article about community gardens?" "To give readers a real person's point of view" "To replace the need for facts" "To make the article shorter" "To hide the central idea" "1" 40
    New-Question "Concept: Poets repeat words for a reason. Question: What is the most likely reason a poet repeats the words ""step by step"" in a poem about climbing a hill?" "To emphasize steady progress" "To tell readers to skip the poem" "To confuse the order of events" "To describe a loud noise" "1" 40
    New-Question "Concept: An author's message can come from the ending. Question: A story ends with neighbors smiling as they share vegetables from a garden they built together. What message is the author most likely sharing?" "Working together can benefit everyone." "Gardens should only grow carrots." "Neighbors need fences between yards." "Vegetables grow best in winter." "1" 40

    New-Question "Concept: Text features help readers find and understand information. Question: Which text feature would best help a reader compare how fast different animals can run?" "a graph" "a chapter title" "a dialogue line" "a cast list" "1" 35
    New-Question "Concept: A timeline shows events in order. Question: Which text feature would best show the order of important events in a scientist's life?" "a timeline" "a caption" "a map" "a glossary" "1" 35
    New-Question "Concept: Diagrams help explain parts of something. Question: Which text feature would best show the parts of a flower?" "a diagram with labels" "a poem" "a table of contents" "a dialogue box" "1" 35
    New-Question "Concept: Captions explain pictures and diagrams. Question: What is the purpose of a caption under a photograph?" "to explain what the picture shows" "to tell the ending of the text" "to list every source used" "to replace the heading" "1" 35
    New-Question "Concept: Headings help readers know what a section is about. Question: What is the purpose of a heading in informational text?" "to tell the topic of a section" "to name the main character" "to give the answer key" "to show who wins a contest" "1" 35
    New-Question "Concept: Bold print helps key words stand out. Question: How does bold print help readers?" "It highlights important words or ideas." "It changes facts into opinions." "It puts events in order." "It replaces diagrams and maps." "1" 35
    New-Question "Concept: Photographs can support understanding. Question: What is the most likely purpose of a photograph in an article about penguins?" "to show what penguins look like" "to list every penguin species" "to tell a make-believe story" "to explain a math problem" "1" 35
    New-Question "Concept: Maps help readers locate places. Question: Which text feature would best help a reader see where deserts are found?" "a map" "a poem stanza" "a glossary entry" "a dialogue line" "1" 35
    New-Question "Concept: Tables help organize facts for comparison. Question: Which text feature would best compare the sizes of three planets?" "a table" "a dedication" "a chapter heading" "a stage direction" "1" 35
    New-Question "Concept: Bullets help present information clearly. Question: Why might an author use bullet points in a nonfiction article?" "To list important facts clearly" "To hide the central idea" "To make the text rhyme" "To show who is speaking" "1" 35
    New-Question "Concept: Italics can help emphasize or identify words. Question: What is the most likely reason an author uses italics for a word in a paragraph?" "To show the word is important or special" "To tell readers to skip the word" "To label a diagram" "To turn the paragraph into poetry" "1" 35
)

$questions += @(
    New-Question "Concept: Labels identify parts in visuals. Question: What is the purpose of labels on a diagram of a bicycle?" "to name each part" "to summarize the whole book" "to show the main character's feelings" "to explain how to write a paragraph" "1" 35

    New-Question "Concept: Figurative language can help readers picture ideas. Question: What is the most likely reason an author writes, ""The cheetah shot forward like an arrow""?" "To highlight how fast the cheetah moved" "To show the cheetah was made of wood" "To explain how arrows are built" "To describe the color of the cheetah" "1" 40
    New-Question "Concept: Onomatopoeia sounds like the noise it names. Question: How does the word ""buzz"" help the reader?" "It helps the reader hear the insect's sound." "It tells the reader the insect is hungry." "It shows the insect is colorful." "It explains where the insect lives." "1" 35
    New-Question "Concept: Imagery appeals to the senses. Question: Which phrase best creates an image of a cold morning?" "icy grass crunching under boots" "a child reading after lunch" "a blue backpack by the desk" "a bell ringing after class" "1" 40
    New-Question "Concept: Sound words can add energy to writing. Question: What is the most likely reason a poet repeats the word ""whoosh"" in a poem about wind?" "To help readers hear the strong wind" "To explain the shape of the clouds" "To show the wind is warm" "To tell the reader the poem is nonfiction" "1" 40
    New-Question "Concept: Similes compare things to make meaning clearer. Question: What is the most likely reason an author writes, ""The pond was smooth as glass""?" "To show how calm the water looked" "To explain how ponds are made" "To tell readers the pond was dangerous" "To show the pond was very deep" "1" 40
    New-Question "Concept: Imagery helps readers picture a scene. Question: Which line best appeals to the sense of hearing?" "The drums thumped through the gym." "The moon glowed above the trees." "The cake looked golden and soft." "The kitten curled on the pillow." "1" 40
    New-Question "Concept: Imagery can help readers visualize a setting. Question: Which phrase best helps the reader picture a sunset?" "orange light spilling across the sky" "books stacked near the wall" "shoes lined up by the door" "pencils rolling off the desk" "1" 40
    New-Question "Concept: Similes can highlight an important quality. Question: What is the most likely reason an author writes, ""The ice cracked like glass""?" "To help readers imagine the sharp breaking sound" "To explain how glass is made" "To show the ice felt warm" "To compare winter to summer" "1" 40
    New-Question "Concept: Onomatopoeia can strengthen sound imagery. Question: What does the word ""clang"" suggest in a story about a fire station?" "a loud metal sound" "a soft whisper" "a bright flash of light" "a smooth gentle movement" "1" 35
    New-Question "Concept: Imagery uses strong details to create pictures in the mind. Question: Which phrase best creates imagery?" "silver rain tapping the window" "interesting facts about spiders" "the title at the top of the page" "students working in groups" "1" 40

    New-Question "Concept: Evidence supports an inference. Question: Which detail best supports the inference that Mia is nervous about speaking?" "Her hands shake as she walks to the microphone." "She wears a red sweater to school." "Her friends sit in the front row." "The room is warm after lunch." "1" 40
    New-Question "Concept: Readers can make inferences from details. Question: Leo packs extra water, a flashlight, and a map before the hike. What can the reader infer?" "Leo is prepared for the trip." "Leo wants to stay home." "Leo has never gone outside." "Leo dislikes the other hikers." "1" 40
    New-Question "Concept: Text evidence supports ideas about characters. Question: Which detail best supports the idea that the two boys are good friends?" "They save each other seats on the bus every day." "They live on the same street." "They both like pizza." "They wear the same team shirt." "1" 40
    New-Question "Concept: Good readers ask questions to deepen understanding. Question: Which question would best help a reader understand the key idea of a section called ""How Seeds Travel""?" "What are some ways seeds move to new places?" "Who drew the picture on the page?" "How many pages are in the book?" "What color are the seeds?" "1" 40
    New-Question "Concept: Evidence can support an inference about a setting. Question: Which detail best supports the idea that a storm is getting closer?" "Thunder rumbles and the sky grows dark." "The grass is bright green." "A bird sits on the fence." "The mailbox is red." "1" 40
    New-Question "Concept: Inferences come from clues in the text. Question: Mr. Chen smiles, claps softly, and says, ""You worked hard for this."" What can the reader infer?" "Mr. Chen is proud." "Mr. Chen is confused." "Mr. Chen is in a hurry." "Mr. Chen is upset." "1" 40
    New-Question "Concept: Readers can connect ideas across texts. Question: Text 1 tells about a girl learning to skateboard. Text 2 tells about a boy practicing piano. Which statement best shows a connection between the texts?" "Both texts show that practice can help people improve." "Both texts are about wild animals." "Both texts explain how machines work." "Both texts describe the same setting." "1" 40
    New-Question "Concept: Asking questions after reading can deepen understanding. Question: After reading an article about sharks, which question would best deepen understanding?" "How do sharks help keep ocean ecosystems balanced?" "What day was the article printed?" "How many letters are in the title?" "What color is the page border?" "1" 40
    New-Question "Concept: Evidence supports an inference about feelings. Question: Which detail best supports the inference that the dog misses its owner?" "The dog waits by the door and whines at every passing car." "The dog has a blue collar." "The dog ate breakfast early." "The dog sleeps on a rug." "1" 40
    New-Question "Concept: Inferences can show character traits. Question: Maya notices a classmate standing alone and invites him to join her group. What can the reader infer about Maya?" "She is kind." "She is impatient." "She is careless." "She is jealous." "1" 40
    New-Question "Concept: Readers can connect text ideas to real life. Question: An article explains how a school garden shares vegetables with families. What is one way this idea can help a community?" "It can provide fresh food for people nearby." "It makes every classroom larger." "It turns summer into winter." "It removes the need for grocery stores." "1" 40
    New-Question "Concept: Evidence should directly support a key idea. Question: Which detail best supports the idea that art can make a garden more interesting?" "Bright mosaics and painted signs add color and design to the space." "Gardens need soil and sunlight to grow." "Many gardens are fenced in for safety." "Watering cans can be made of metal." "1" 40
    New-Question "Concept: Inferences come from actions and clues. Question: A student rewrites his paragraph three times and asks for feedback each time. What can the reader infer?" "He wants to improve his work." "He is ready to quit writing." "He does not care about the assignment." "He forgot the topic." "1" 40
    New-Question "Concept: Good readers ask questions while reading. Question: Which question would best guide reading a section called ""Life in the Desert""?" "How do plants and animals survive with little water?" "What color is the cover of the book?" "Who sharpened the author's pencils?" "How many words are on the page?" "1" 40
)

Add-QuestionBlock @'
Concept: The suffix -less means without. Question: What does painless mean?|||without pain|||full of pain|||pain before|||pain again|||1|||35
Concept: The suffix -less means without. Question: What does spotless mean?|||full of spots|||covered by spots|||without spots|||spot again|||3|||35
Concept: The suffix -less means without. Question: What does sleepless mean?|||without sleep|||full of sleep|||before sleep|||sleeping again|||1|||35
Concept: The suffix -less means without. Question: What does fearless mean?|||full of fear|||without fear|||fear before|||fear again|||2|||35
Concept: The suffix -less means without. Question: What does careless mean?|||with great care|||without care|||care after|||care before|||2|||35
Concept: The suffix -less means without. Question: What does harmless mean?|||without harm|||full of harm|||harm again|||harm before|||1|||35
Concept: The suffix -less means without. Question: What does powerless mean?|||full of power|||power again|||without power|||before power|||3|||35
Concept: The suffix -less means without. Question: What does endless mean?|||with an ending|||before the end|||ending again|||without end|||4|||35
Concept: The suffix -ful means full of. Question: What does thankful mean?|||without thanks|||full of thanks|||thanks again|||thanks before|||2|||35
Concept: The suffix -ful means full of. Question: What does careful mean?|||without care|||full of care|||care too late|||care before|||2|||35
Concept: The suffix -ful means full of. Question: What does playful mean?|||full of play|||without play|||play before|||play again|||1|||35
Concept: The suffix -ful means full of. Question: What does useful mean?|||full of use|||without use|||used before|||used again|||1|||35
Concept: The suffix -ful means full of. Question: What does colorful mean?|||without color|||full of color|||colored before|||colored again|||2|||35
Concept: The suffix -ful means full of. Question: What does peaceful mean?|||full of peace|||without peace|||peace before|||peace again|||1|||35
Concept: The suffix -ful means full of. Question: What does helpful mean?|||without help|||help again|||full of help|||help before|||3|||35
Concept: The suffix -ful means full of. Question: What does truthful mean?|||full of truth|||without truth|||truth before|||truth again|||1|||35
Concept: The suffix -ness names a state or condition. Question: What does darkness mean?|||the state of being dark|||without dark|||before dark|||dark again|||1|||35
Concept: The suffix -ness names a state or condition. Question: What does kindness mean?|||the state of being kind|||not kind|||kind before|||kind again|||1|||35
Concept: The suffix -ness names a state or condition. Question: What does sickness mean?|||the state of being sick|||before being sick|||full of medicine|||not sick|||1|||35
Concept: The suffix -ness names a state or condition. Question: What does weakness mean?|||the state of being weak|||without weakness|||weak again|||before weak|||1|||35
Concept: The suffix -ness names a state or condition. Question: What does softness mean?|||the state of being soft|||not soft|||before soft|||soft again|||1|||35
Concept: The suffix -ness names a state or condition. Question: What does sadness mean?|||the state of being sad|||without sadness|||sad before|||sad again|||1|||35
Concept: The suffix -ness names a state or condition. Question: What does stillness mean?|||the state of being still|||moving quickly|||without stillness|||still again|||1|||35
Concept: The suffix -ness names a state or condition. Question: What does brightness mean?|||the state of being bright|||without light|||before bright|||bright again|||1|||35
Concept: The suffix -y can mean full of. Question: What does rainy mean?|||without rain|||rain before|||full of rain|||rain again|||3|||35
Concept: The suffix -y can mean full of. Question: What does snowy mean?|||before snow|||full of snow|||snow again|||without snow|||2|||35
Concept: The suffix -y can mean full of. Question: What does muddy mean?|||full of mud|||without mud|||mud before|||mud again|||1|||35
Concept: The suffix -y can mean full of. Question: What does dusty mean?|||dust again|||without dust|||full of dust|||before dust|||3|||35
Concept: The suffix -y can mean full of. Question: What does foggy mean?|||before fog|||full of fog|||without fog|||fog again|||2|||35
Concept: The suffix -y can mean full of. Question: What does rocky mean?|||full of rocks|||without rocks|||before rocks|||rocks again|||1|||35
Concept: The suffix -y can mean full of. Question: What does noisy mean?|||quiet|||full of noise|||before noise|||noise again|||2|||35
Concept: The suffix -y can mean full of. Question: What does windy mean?|||without wind|||full of wind|||wind again|||wind before|||2|||35
Concept: The prefix pre- means before. Question: What does preview mean?|||to view after|||to view before|||to view without|||to view again|||2|||35
Concept: The prefix pre- means before. Question: What does preheat mean?|||to heat before|||to heat later|||to heat without|||to heat again|||1|||35
Concept: The prefix pre- means before. Question: What does preschool mean?|||school before first grade|||school after college|||school without teachers|||school only at night|||1|||35
Concept: The prefix pre- means before. Question: What does pretest mean?|||a test after learning|||a test before the main lesson or unit|||a test with no questions|||a test repeated twice|||2|||35
Concept: The prefix dis- often means not. Question: What does dislike mean?|||to like a lot|||to not like|||to like before|||to like again|||2|||35
Concept: The prefix dis- often means not. Question: What does dishonest mean?|||not honest|||very honest|||honest again|||honest before|||1|||35
Concept: The prefix dis- often means not. Question: What does disobey mean?|||to obey quickly|||to obey later|||to not obey|||to obey again|||3|||35
Concept: The prefix dis- often means not. Question: What does disagree mean?|||to agree strongly|||to not agree|||to agree later|||to agree again|||2|||35
Concept: The prefix in- often means not. Question: What does incorrect mean?|||correct again|||very correct|||not correct|||correct before|||3|||35
Concept: The prefix in- often means not. Question: What does inactive mean?|||active again|||not active|||active before|||very active|||2|||35
Concept: The prefix in- often means not. Question: What does incomplete mean?|||finished all the way|||not complete|||complete again|||complete before|||2|||35
Concept: The prefix in- often means not. Question: What does invisible mean?|||easy to see|||seen before|||not visible|||visible again|||3|||35
Concept: The prefix non- means not. Question: What does nonfiction mean?|||not fiction|||fiction again|||fiction before|||full of fiction|||1|||35
Concept: The prefix non- means not. Question: What does nonstop mean?|||without stopping|||stopping before|||stopping again|||easy to stop|||1|||35
Concept: The prefix im- often means not. Question: What does impossible mean?|||possible again|||not possible|||possible before|||very possible|||2|||35
Concept: The prefix im- often means not. Question: What does impatient mean?|||full of patience|||not patient|||patient before|||patient again|||2|||35
Concept: The prefix im- often means not. Question: What does impolite mean?|||polite again|||very polite|||not polite|||polite before|||3|||35
Concept: The prefix im- often means not. Question: What does immature mean?|||not mature|||mature again|||mature before|||very mature|||1|||35
'@

Add-QuestionBlock @'
Concept: A synonym has almost the same meaning. Question: Which word is a synonym for rapid?|||quick|||sleepy|||careful|||quiet|||1|||35
Concept: A synonym has almost the same meaning. Question: Which word is a synonym for silent?|||bright|||quiet|||rough|||crowded|||2|||35
Concept: A synonym has almost the same meaning. Question: Which word is a synonym for begin?|||finish|||start|||sleep|||hide|||2|||35
Concept: A synonym has almost the same meaning. Question: Which word is a synonym for ancient?|||modern|||old|||tiny|||smooth|||2|||35
Concept: A synonym has almost the same meaning. Question: Which word is a synonym for narrow?|||wide|||thin|||loud|||gentle|||2|||35
Concept: A synonym has almost the same meaning. Question: Which word is a synonym for sturdy?|||weak|||strong|||slippery|||angry|||2|||35
Concept: A synonym has almost the same meaning. Question: Which word is a synonym for vanish?|||appear|||disappear|||stretch|||wander|||2|||35
Concept: A synonym has almost the same meaning. Question: Which word is a synonym for clever?|||smart|||sleepy|||messy|||plain|||1|||35
Concept: A synonym has almost the same meaning. Question: Which word is a synonym for purchase?|||buy|||lose|||borrow|||drop|||1|||35
Concept: A synonym has almost the same meaning. Question: Which word is a synonym for choose?|||guess|||pick|||push|||forget|||2|||35
Concept: A synonym has almost the same meaning. Question: Which word is a synonym for gentle?|||soft|||wild|||loud|||empty|||1|||35
Concept: A synonym has almost the same meaning. Question: Which word is a synonym for enormous?|||tiny|||huge|||clear|||narrow|||2|||35
Concept: A synonym has almost the same meaning. Question: Which word is a synonym for reply?|||question|||answer|||paint|||climb|||2|||35
Concept: A synonym has almost the same meaning. Question: Which word is a synonym for peaceful?|||calm|||stormy|||dusty|||hungry|||1|||35
Concept: A synonym has almost the same meaning. Question: Which word is a synonym for cheerful?|||angry|||happy|||plain|||shallow|||2|||35
Concept: A synonym has almost the same meaning. Question: Which word is a synonym for repair?|||break|||fix|||shake|||measure|||2|||35
Concept: A synonym has almost the same meaning. Question: Which word is a synonym for tiny?|||heavy|||small|||noisy|||fancy|||2|||35
Concept: A synonym has almost the same meaning. Question: Which word is a synonym for discover?|||hide|||find|||erase|||miss|||2|||35
Concept: A synonym has almost the same meaning. Question: Which word is a synonym for protect?|||guard|||scatter|||melt|||trade|||1|||35
Concept: A synonym has almost the same meaning. Question: Which word is a synonym for ordinary?|||common|||glittering|||brave|||stormy|||1|||35
Concept: A synonym has almost the same meaning. Question: Which word is a synonym for furious?|||angry|||careful|||tidy|||quick|||1|||35
Concept: A synonym has almost the same meaning. Question: Which word is a synonym for glossy?|||shiny|||rough|||sleepy|||dark|||1|||35
Concept: A synonym has almost the same meaning. Question: Which word is a synonym for difficult?|||easy|||hard|||gentle|||open|||2|||35
Concept: A synonym has almost the same meaning. Question: Which word is a synonym for damp?|||dry|||slightly wet|||loud|||careful|||2|||35
Concept: A synonym has almost the same meaning. Question: Which word is a synonym for fragile?|||strong|||easy to break|||smooth|||wide|||2|||35

Concept: An antonym is the opposite of a word. Question: Which word is an antonym of ancient?|||new|||old|||wide|||late|||1|||35
Concept: An antonym is the opposite of a word. Question: Which word is an antonym of generous?|||kind|||selfish|||friendly|||helpful|||2|||35
Concept: An antonym is the opposite of a word. Question: Which word is an antonym of noisy?|||quiet|||crowded|||bright|||messy|||1|||35
Concept: An antonym is the opposite of a word. Question: Which word is an antonym of cloudy?|||stormy|||clear|||dusty|||dark|||2|||35
Concept: An antonym is the opposite of a word. Question: Which word is an antonym of narrow?|||slim|||wide|||gentle|||silent|||2|||35
Concept: An antonym is the opposite of a word. Question: Which word is an antonym of empty?|||blank|||full|||smooth|||near|||2|||35
Concept: An antonym is the opposite of a word. Question: Which word is an antonym of early?|||late|||first|||sunny|||quick|||1|||35
Concept: An antonym is the opposite of a word. Question: Which word is an antonym of rough?|||sharp|||smooth|||dusty|||plain|||2|||35
Concept: An antonym is the opposite of a word. Question: Which word is an antonym of safe?|||dangerous|||simple|||calm|||silent|||1|||35
Concept: An antonym is the opposite of a word. Question: Which word is an antonym of strong?|||solid|||weak|||sturdy|||ready|||2|||35
Concept: An antonym is the opposite of a word. Question: Which word is an antonym of cheerful?|||happy|||sad|||excited|||thankful|||2|||35
Concept: An antonym is the opposite of a word. Question: Which word is an antonym of careful?|||quiet|||careless|||sleepy|||common|||2|||35
Concept: An antonym is the opposite of a word. Question: Which word is an antonym of open?|||bright|||closed|||large|||brave|||2|||35
Concept: An antonym is the opposite of a word. Question: Which word is an antonym of above?|||below|||near|||through|||beside|||1|||35
Concept: An antonym is the opposite of a word. Question: Which word is an antonym of gentle?|||harsh|||kind|||slow|||smooth|||1|||35
Concept: An antonym is the opposite of a word. Question: Which word is an antonym of bright?|||shiny|||dim|||clear|||sunny|||2|||35
Concept: An antonym is the opposite of a word. Question: Which word is an antonym of victory?|||defeat|||cheer|||contest|||prize|||1|||35
Concept: An antonym is the opposite of a word. Question: Which word is an antonym of ancient?|||modern|||old|||empty|||brave|||1|||35
Concept: An antonym is the opposite of a word. Question: Which word is an antonym of timid?|||quiet|||brave|||sleepy|||gentle|||2|||35
Concept: An antonym is the opposite of a word. Question: Which word is an antonym of include?|||invite|||exclude|||gather|||cover|||2|||35
Concept: An antonym is the opposite of a word. Question: Which word is an antonym of bright?|||dark|||sunny|||clear|||glossy|||1|||35
Concept: An antonym is the opposite of a word. Question: Which word is an antonym of improve?|||repair|||worsen|||build|||practice|||2|||35
Concept: An antonym is the opposite of a word. Question: Which word is an antonym of upward?|||outward|||downward|||nearby|||faster|||2|||35
Concept: An antonym is the opposite of a word. Question: Which word is an antonym of fresh?|||stale|||cool|||light|||soft|||1|||35
Concept: An antonym is the opposite of a word. Question: Which word is an antonym of ancient?|||brand-new|||historic|||aged|||dusty|||1|||35
'@

Add-QuestionBlock @'
Concept: Some words have more than one meaning. Question: In the sentence "They sat on the bank of the river," what does bank mean?|||a place for money|||the edge of land by water|||a row of chairs|||a pile of snow|||2|||40
Concept: Some words have more than one meaning. Question: In the sentence "The bark on the tree felt rough," what does bark mean?|||the sound a dog makes|||the outer covering of a tree|||a quick jump|||a kind of leaf|||2|||40
Concept: Some words have more than one meaning. Question: In the sentence "This backpack is light," what does light mean?|||not heavy|||a lamp|||a bright flash|||fire from a match|||1|||40
Concept: Some words have more than one meaning. Question: In the sentence "A bat flew out of the cave," what does bat mean?|||a flying animal|||sports equipment|||a small boat|||a hat|||1|||40
Concept: Some words have more than one meaning. Question: In the sentence "Flowers bloom in spring," what does spring mean?|||a metal coil|||a season|||a quick jump|||a deep well|||2|||40
Concept: Some words have more than one meaning. Question: In the sentence "The traffic jam made us late," what does jam mean?|||fruit spread|||cars stuck together|||a loud song|||a metal tool|||2|||40
Concept: Some words have more than one meaning. Question: In the sentence "What kind of bird is that?" what does kind mean?|||nice behavior|||a type|||a loud sound|||a small gift|||2|||40
Concept: Some words have more than one meaning. Question: In the sentence "Watch the turtle cross the path," what does watch mean?|||a timepiece|||to look carefully|||to fix something|||to turn around|||2|||40
Concept: Some words have more than one meaning. Question: In the sentence "We heard the ring of the bell," what does ring mean?|||a piece of jewelry|||a circular mark|||a sound|||a game|||3|||40
Concept: Some words have more than one meaning. Question: In the sentence "The teacher made a fair rule," what does fair mean?|||just|||light-colored|||a carnival|||windy|||1|||40
Concept: Some words have more than one meaning. Question: In the sentence "Be careful not to trip on the rug," what does trip mean?|||a journey|||to stumble|||a shoe|||to clap loudly|||2|||40
Concept: Some words have more than one meaning. Question: In the sentence "These socks match," what does match mean?|||to go together|||a stick for fire|||a sports game|||to smell alike|||1|||40
Concept: Some words have more than one meaning. Question: In the sentence "Duck when the ball comes close!" what does duck mean?|||a bird|||to lower your head|||to swim slowly|||to call for help|||2|||40
Concept: Some words have more than one meaning. Question: In the sentence "Please seal the box," what does seal mean?|||an ocean animal|||to close tightly|||to draw a circle|||to carry outside|||2|||40
Concept: Some words have more than one meaning. Question: In the sentence "Mom left a note on the table," what does note mean?|||a short message|||a loud song|||a shiny coin|||a warm blanket|||1|||40
Concept: Some words have more than one meaning. Question: In the sentence "The elephant lifted its trunk," what does trunk mean?|||a large nose-like body part|||a suitcase|||the middle of a tree|||a road sign|||1|||40
Concept: Some words have more than one meaning. Question: In the sentence "The leaves began to fall," what does leaves mean?|||parts of a tree|||goes away|||green paint|||small flowers|||1|||40
Concept: Some words have more than one meaning. Question: In the sentence "The current in the river was strong," what does current mean?|||happening now|||flow of water|||electrical power|||a gift|||2|||40
Concept: Some words have more than one meaning. Question: In the sentence "The pencil has a sharp point," what does point mean?|||to aim a finger|||the sharp end|||a reason to argue|||a score in a game|||2|||40
Concept: Some words have more than one meaning. Question: In the sentence "A metal can rolled across the floor," what does can mean?|||to be able to|||a container|||a loud noise|||to stop|||2|||40
Concept: Some words have more than one meaning. Question: In the sentence "We will park beside the store," what does park mean?|||an area with swings and trees|||to leave a car in one place|||to run in a race|||to draw a map|||2|||40
Concept: Some words have more than one meaning. Question: In the sentence "A row of chairs lined the wall," what does row mean?|||a noisy argument|||a straight line|||to move a boat|||a piece of rope|||2|||40
Concept: Some words have more than one meaning. Question: In the sentence "Please check your answers," what does check mean?|||paper used to pay|||to look over carefully|||to stop moving|||to close a door|||2|||40
Concept: Some words have more than one meaning. Question: In the sentence "The crowd gave a wave as the bus left," what does wave mean?|||a motion with the hand|||water moving in the sea|||a kind of plant|||a piece of cloth|||1|||40
Concept: Some words have more than one meaning. Question: In the sentence "It takes time to train a puppy," what does train mean?|||a long vehicle on tracks|||to teach through practice|||to tie with rope|||to paint carefully|||2|||40
Concept: Some words have more than one meaning. Question: In the sentence "There was only one cookie left," what does left mean?|||opposite of right|||remaining|||went away|||slow to move|||2|||40
Concept: Some words have more than one meaning. Question: In the sentence "Mila chose the right answer," what does right mean?|||the opposite of left|||correct|||fair|||bright|||2|||40
Concept: Some words have more than one meaning. Question: In the sentence "Put the papers in the file," what does file mean?|||a tool with rough edges|||a folder for papers|||to walk in a line|||a noisy machine|||2|||40
Concept: Some words have more than one meaning. Question: In the sentence "The chess club meets after school," what does club mean?|||a heavy stick|||a group with the same interest|||a dance move|||a kind of cap|||2|||40
Concept: Some words have more than one meaning. Question: In the sentence "Circle the date on the calendar," what does date mean?|||a kind of fruit|||the day and month|||a place to sit|||a loud sound|||2|||40
Concept: Some words have more than one meaning. Question: In the sentence "Jada is a bright student," what does bright mean?|||shining with light|||smart|||very noisy|||full of color|||2|||40
Concept: Some words have more than one meaning. Question: In the sentence "A pitcher of lemonade sat on the table," what does pitcher mean?|||a baseball player|||a large container for pouring drinks|||a type of hat|||a scorekeeper|||2|||40
Concept: Some words have more than one meaning. Question: In the sentence "The ruler measured the line," what does ruler mean?|||a person in charge of a country|||a measuring tool|||a sharp pencil|||a sheet of paper|||2|||40
Concept: Some words have more than one meaning. Question: In the sentence "The nail bent when it hit the wood," what does nail mean?|||part of a finger|||a small metal fastener|||a kind of brush|||a tree branch|||2|||40
Concept: Some words have more than one meaning. Question: In the sentence "The teams ended with a tie," what does tie mean?|||a neckpiece|||the same score|||to fasten with string|||to turn a page|||2|||40
Concept: Some words have more than one meaning. Question: In the sentence "I am a big fan of that team," what does fan mean?|||a tool that blows air|||someone who really likes something|||a kind of bird|||a paper chart|||2|||40
Concept: Some words have more than one meaning. Question: In the sentence "She held the shell in her palm," what does palm mean?|||a kind of tree|||the inside of a hand|||a large leaf|||the bottom of a shoe|||2|||40
Concept: Some words have more than one meaning. Question: In the sentence "We will order our lunch now," what does order mean?|||arrangement of things|||to ask for food|||to clean the table|||to write a poem|||2|||40
Concept: Some words have more than one meaning. Question: In the sentence "They boarded the train at noon," what does board mean?|||a flat piece of wood|||to get on a vehicle|||to draw a line|||to close a window|||2|||40
Concept: Some words have more than one meaning. Question: In the sentence "The store gave Mom her change," what does change mean?|||to become different|||money returned after paying|||to trade places|||to shift a chair|||2|||40
Concept: Some words have more than one meaning. Question: In the sentence "A cold draft came under the door," what does draft mean?|||a first version of writing|||cool moving air|||a group of horses|||a deep puddle|||2|||40
Concept: Some words have more than one meaning. Question: In the sentence "The crane lifted the steel beam," what does crane mean?|||a tall bird|||a machine for lifting heavy things|||a kind of truck tire|||a river crossing|||2|||40
Concept: Some words have more than one meaning. Question: In the sentence "The players ran onto the court," what does court mean?|||a place for sports games|||a judge's room|||a kind of blanket|||a high hill|||1|||40
Concept: Some words have more than one meaning. Question: In the sentence "There is a bug in the computer program," what does bug mean?|||an insect|||a problem or mistake|||a loud beep|||a tiny battery|||2|||40
Concept: Some words have more than one meaning. Question: In the sentence "The batter held the bat tightly," what does bat mean?|||a flying animal|||sports equipment used to hit a ball|||a winter coat|||a long rope|||2|||40
Concept: Some words have more than one meaning. Question: In the sentence "The star of the play took a bow," what does star mean?|||a shape in the sky|||the main performer|||a shiny sticker|||a science tool|||2|||40
Concept: Some words have more than one meaning. Question: In the sentence "The coach left after the game," what does coach mean?|||a sports leader|||a long bus|||a small bag|||a school subject|||1|||40
Concept: Some words have more than one meaning. Question: In the sentence "Please file into the room quietly," what does file mean?|||to move in a line|||a folder for papers|||a rough metal tool|||a type of game|||1|||40
Concept: Some words have more than one meaning. Question: In the sentence "The rock boat began to rock in the wind," what does rock mean in the second use?|||a stone|||to move back and forth|||to sing loudly|||to close tightly|||2|||40
Concept: Some words have more than one meaning. Question: In the sentence "The captain will point to the map," what does point mean?|||a sharp end|||to aim with a finger|||a score in a game|||an important idea|||2|||40
Concept: Some words have more than one meaning. Question: In the sentence "The check arrived at the restaurant table," what does check mean?|||a careful look|||paper that shows the amount to pay|||a game mark|||a stopped motion|||2|||40
'@

Add-QuestionBlock @'
Concept: Genre clues help readers identify realistic fiction. Question: Which sentence is most likely from realistic fiction?|||Jordan forgot his homework on the bus.|||A dragon guarded the silver bridge.|||The moon whispered to the stars.|||A pencil danced across the desk.|||1|||35
Concept: Genre clues help readers identify fantasy. Question: Which sentence is most likely from fantasy?|||The class planted beans in cups.|||A rabbit wore boots and spoke to the mayor.|||Mom packed sandwiches for lunch.|||The team practiced after school.|||2|||35
Concept: A biography tells the true story of a real person. Question: Which title is most likely a biography?|||The Life of Ruby Bridges|||The Secret of the Talking Tree|||How to Bake Muffins|||Poems for Windy Days|||1|||35
Concept: In a drama, characters speak the lines. Question: Which feature belongs to a play?|||stage directions|||a glossary|||a recipe list|||a bar graph|||1|||35
Concept: Poetry often uses lines and rhythm. Question: Which feature is common in poetry?|||short lines|||chapter numbers only|||step-by-step directions|||caption boxes|||1|||35
Concept: A folktale is often passed down and teaches a lesson. Question: Which idea best shows that a story is a folktale?|||It teaches a lesson through events.|||It lists facts about frogs.|||It explains how to build a kite.|||It gives directions for a game.|||1|||35
Concept: Informational text teaches with facts. Question: Which sentence is most likely from informational text?|||Some frogs can leap many times their body length.|||The pond sang a sleepy song.|||A giant turtle wore a crown.|||Maya wished the clouds could talk.|||1|||35
Concept: Persuasive text tries to convince the reader. Question: Which sentence is most likely from persuasive writing?|||You should bring a reusable bottle to school each day.|||Bees carry pollen from flower to flower.|||The squirrel found an acorn near the tree.|||The poem has four short lines.|||1|||35
Concept: Authors write to inform, entertain, or persuade. Question: An article explains how clouds form. What is the author's purpose?|||to inform|||to entertain|||to persuade|||to confuse|||1|||35
Concept: Authors sometimes persuade readers to act. Question: A poster says, "Join the cleanup team this Saturday!" What is the author's purpose?|||to persuade|||to entertain|||to inform only|||to retell a folktale|||1|||35

Concept: Authors use visuals for a reason. Question: What is the most likely reason an author includes a photograph in an article about penguins?|||To show what penguins look like|||To replace all written facts|||To introduce a fictional hero|||To hide the central idea|||1|||40
Concept: Headings help organize information. Question: What is the purpose of a heading called "Food and Shelter" in an animal article?|||To show what the section is mostly about|||To tell the ending of the article|||To list the author's favorite animals|||To explain a simile|||1|||40
Concept: Bold print helps important words stand out. Question: Why might an author print the word "habitat" in bold?|||To highlight an important word|||To turn the article into poetry|||To hide a clue from readers|||To show the text is fantasy|||1|||40
Concept: Captions explain visuals. Question: What is the purpose of a caption under a diagram?|||To explain the visual|||To give the answer key|||To name the author only|||To show a new chapter begins|||1|||35
Concept: Diagrams help readers see parts or steps. Question: Which text feature would best show the parts of a bicycle?|||a labeled diagram|||a poem stanza|||a cast list|||a chapter title|||1|||35
Concept: A graph helps compare numbers. Question: Which text feature would best compare how many books four classes read?|||a graph|||a dialogue line|||a glossary|||a scene heading|||1|||35
Concept: A table helps organize facts for comparison. Question: Which text feature would best compare the heights of three mountains?|||a table|||a dedication|||a subtitle only|||a speech bubble|||1|||35
Concept: Maps help readers locate places. Question: Which text feature would best help a reader see where deserts are located?|||a map|||a poem|||a cast list|||a paragraph label|||1|||35
Concept: Timelines show events in order. Question: Which text feature would best show the order of important events in a person's life?|||a timeline|||a diagram|||a glossary|||a map key|||1|||35
Concept: A glossary explains special words. Question: What is the purpose of a glossary in nonfiction?|||To define important words|||To list every chapter title|||To show the ending first|||To compare numbers in a chart|||1|||35

Concept: Evidence supports an inference. Question: Which detail best supports the inference that Ava is nervous before the recital?|||Her hands shake as she walks to the stage.|||Her dress is blue.|||Her grandma sits in the front row.|||The piano is polished.|||1|||40
Concept: Readers can infer ideas from clues. Question: Leo packs a raincoat, boots, and an umbrella before school. What can the reader infer?|||Leo expects rainy weather.|||Leo is going swimming.|||Leo forgot his homework.|||Leo dislikes cold drinks.|||1|||40
Concept: Text evidence supports ideas about feelings. Question: Which detail best supports the idea that Mr. Chen is proud?|||He smiles and claps after the project is finished.|||He wears a green shirt.|||He places books on a shelf.|||He walks to the window.|||1|||40
Concept: Readers can connect ideas across texts. Question: Text 1 is about learning piano. Text 2 is about learning soccer. Which statement best shows a connection between the texts?|||Both texts show that practice helps people improve.|||Both texts are about wild animals.|||Both texts explain how machines work.|||Both texts describe the same setting.|||1|||40
Concept: Good readers ask questions to deepen understanding. Question: Which question would best help a reader understand a section called "How Seeds Travel"?|||What are some ways seeds move to new places?|||What color is the cover?|||Who sharpened the pencils?|||How many words are in the title?|||1|||40
Concept: Evidence can support an inference about a setting. Question: Which detail best supports the idea that a storm is getting closer?|||Thunder rumbles and the sky grows dark.|||A bird sits on a fence.|||The mailbox is red.|||The grass is green.|||1|||40
Concept: Inferences can reveal character traits. Question: Maya notices a classmate alone and invites him to join her group. What can the reader infer about Maya?|||She is kind.|||She is impatient.|||She is careless.|||She is jealous.|||1|||40
Concept: Evidence supports a key idea. Question: Which detail best supports the idea that art can make a garden more interesting?|||Bright mosaics and painted signs add color to the space.|||Gardens need soil and water to grow.|||Many gardens use fences for safety.|||Some watering cans are metal.|||1|||40
Concept: Inferences come from actions and clues. Question: A student rewrites a paragraph three times and asks for feedback each time. What can the reader infer?|||He wants to improve his work.|||He is ready to quit.|||He does not care about the assignment.|||He forgot the topic.|||1|||40
Concept: Text evidence can support an idea about friendship. Question: Which detail best supports the idea that two students work well together?|||They take turns carrying supplies for the project.|||They sit near the same window.|||They both wear sneakers.|||They each bring lunch from home.|||1|||40

Concept: Theme is the lesson or message of a story. Question: A child keeps practicing a skateboard trick and finally lands it. Which theme best fits the story?|||Practice can lead to success.|||Skateboards should be painted bright colors.|||Parks need more benches.|||Friends must always agree.|||1|||40
Concept: Theme tells what readers can learn from a story. Question: A girl tells the truth after breaking a vase and feels relieved. Which theme best fits the story?|||Honesty matters.|||Vases are hard to replace.|||Homes should have fewer shelves.|||Mistakes never happen.|||1|||40
Concept: Theme can come from acts of kindness. Question: A class helps a new student learn routines and feel welcome. Which theme best fits the story?|||Kindness helps others feel included.|||Classrooms should be larger.|||Schools need more bells.|||Rules are always confusing.|||1|||40
Concept: Character relationships show how people feel toward each other. Question: Ava asks Grandpa to read her writing because she values his advice. Which statement best describes their relationship?|||Ava trusts Grandpa's opinion.|||Ava wants to avoid Grandpa.|||Grandpa is annoyed by Ava.|||Ava does not listen to Grandpa.|||1|||40
Concept: Character traits can be inferred from behavior. Question: Mei keeps practicing the piano piece even when it is difficult. Which trait best describes Mei?|||determined|||careless|||lazy|||forgetful|||1|||35
Concept: Plot includes the main problem, events, and solution. Question: Which event best shows the conflict in a story about a lost backpack?|||Lena cannot find the backpack before the bus arrives.|||Lena packs two notebooks.|||Lena ties her shoes.|||Lena waves to her neighbor.|||1|||40
Concept: Resolution shows how a problem is solved. Question: Which event best shows the resolution in a story about a broken fence?|||The family repairs the fence and the dog stays safe in the yard.|||The dog barks near the gate.|||The family notices a loose board.|||The yard has green grass.|||1|||40
Concept: Sequence helps readers know what happens next. Question: Which event would most likely happen after a class gathers ingredients for muffins?|||The batter is mixed in a bowl.|||The muffins cool on a rack.|||The class eats the muffins.|||The recipe card is put away.|||1|||35
Concept: Conflict can grow as new problems appear. Question: Which event adds to the conflict in a story about a science fair project?|||The volcano model cracks the night before the fair.|||The table is covered with paper.|||The ribbon is blue.|||The teacher smiles at the class.|||1|||40
Concept: Central idea is the main point of an informational text. Question: Which sentence best states a central idea for an article about recycling?|||Recycling helps reduce waste and reuse materials.|||The blue bin is near the wall.|||One student collected cans yesterday.|||Some paper is white and some is brown.|||1|||40

Concept: Supporting details prove a central idea. Question: Which detail best supports the idea that bees help plants grow?|||Bees carry pollen from flower to flower.|||Bees can be yellow and black.|||Some bees live in hives.|||A bee has six legs.|||1|||40
Concept: Central idea tells what the text mostly teaches. Question: Which sentence best states a central idea for an article about maps?|||Maps help people understand where places are.|||Some maps use blue for water.|||One map hangs by the door.|||The classroom globe is round.|||1|||40
Concept: Readers can identify details that do not support a key idea. Question: Which detail does NOT support the idea that school gardens teach responsibility?|||Students remember to water the plants.|||Students pull weeds from the beds.|||Students watch seeds sprout over time.|||The gym floor was polished on Monday.|||4|||40
Concept: Central idea can connect to science and history topics. Question: Which sentence best states a central idea for an article about fossils?|||Fossils give clues about plants and animals from long ago.|||Some fossils are very small.|||Scientists use brushes and tools.|||A fossil can be found in rock.|||1|||40
Concept: Good readers ask questions after reading. Question: After reading an article about sharks, which question would best deepen understanding?|||How do sharks help keep ocean ecosystems balanced?|||What day was the article printed?|||How many letters are in the title?|||What color is the page border?|||1|||40
Concept: Readers can connect text ideas to real life. Question: An article explains how a school garden shares vegetables with families. What is one way this idea can help a community?|||It can provide fresh food for people nearby.|||It makes every classroom larger.|||It removes the need for stores.|||It turns summer into winter.|||1|||40
Concept: Text features support understanding. Question: Which text feature would best show the parts of a plant?|||a labeled diagram|||a paragraph summary|||a dialogue line|||a scene heading|||1|||35
Concept: Authors include quotations for a reason. Question: What is the most likely reason an author includes a gardener's quote in an article about community gardens?|||To give a real person's point of view|||To replace all the facts|||To hide the central idea|||To make the article shorter only|||1|||40
Concept: Authors use repeated words to add meaning. Question: What is the most likely reason a poet repeats the words "step by step" in a poem about climbing a hill?|||To emphasize steady progress|||To confuse the order of events|||To describe a loud noise|||To tell readers to skip the poem|||1|||40
Concept: Visuals can support an author's purpose. Question: What is the most likely reason an author includes a photograph at the beginning of a garden article?|||To show what the garden looks like before readers learn more about it|||To replace all the written information|||To introduce a fictional character|||To reveal the ending immediately|||1|||40
'@

function Get-ShuffledAnswerSet {
    param(
        [Parameter(Mandatory = $true)]
        $QuestionItem
    )

    $answerEntries = @()
    for ($i = 0; $i -lt $QuestionItem.answers.Count; $i++) {
        $answerEntries += [pscustomobject]@{
            Text      = [string]$QuestionItem.answers[$i]
            IsCorrect = ([string]($i + 1) -eq [string]$QuestionItem.correct)
        }
    }

    $shuffledEntries = @($answerEntries | Sort-Object { Get-Random })
    $correctIndex = 1

    for ($i = 0; $i -lt $shuffledEntries.Count; $i++) {
        if ($shuffledEntries[$i].IsCorrect) {
            $correctIndex = $i + 1
            break
        }
    }

    [pscustomobject]@{
        Answers = @($shuffledEntries | ForEach-Object { $_.Text })
        Correct = [string]$correctIndex
    }
}

$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false

try {
    $workbook = $excel.Workbooks.Open($SourceWorkbook)
    $worksheet = $workbook.Worksheets.Item(1)

    $worksheet.Range("A3:H1000").ClearContents()

    $row = 3
    $questionNumber = 1
    foreach ($item in $questions) {
        $shuffledAnswerSet = Get-ShuffledAnswerSet -QuestionItem $item
        $answers = @($shuffledAnswerSet.Answers)
        while ($answers.Count -lt 4) {
            $answers += ""
        }

        $worksheet.Cells.Item($row, 1).Value = [int]$questionNumber
        $worksheet.Cells.Item($row, 2).Value = [string]$item.question
        $worksheet.Cells.Item($row, 3).Value = [string]$answers[0]
        $worksheet.Cells.Item($row, 4).Value = [string]$answers[1]
        $worksheet.Cells.Item($row, 5).Value = [string]$answers[2]
        $worksheet.Cells.Item($row, 6).Value = [string]$answers[3]
        $worksheet.Cells.Item($row, 7).Value = [int]$item.time
        $worksheet.Cells.Item($row, 8).Value = [string]$shuffledAnswerSet.Correct
        $row++
        $questionNumber++
    }

    $workbook.SaveAs($OutputWorkbook, 51)
    $workbook.Close($false)

    Write-Output "Created: $OutputWorkbook"
    Write-Output "Question count: $($questions.Count)"
}
finally {
    if ($worksheet) {
        [System.Runtime.InteropServices.Marshal]::ReleaseComObject($worksheet) | Out-Null
    }
    if ($workbook) {
        [System.Runtime.InteropServices.Marshal]::ReleaseComObject($workbook) | Out-Null
    }
    $excel.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($excel) | Out-Null
    [gc]::Collect()
    [gc]::WaitForPendingFinalizers()
}
