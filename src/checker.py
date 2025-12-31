"""Sends Esperanto text to Gemini Pro for grammar and spelling checking."""

import os
from google import genai
from google.genai import types


def check(text: str) -> None:
    """Check the text for grammar and spelling errors using Gemini Pro."""

    api_key = os.environ.get("GEMINI_API_KEY")
    print("API Key: ", api_key)
    client = genai.Client(api_key=api_key)

    formatting = """The output should be formatted in a JSON list. Note that every piece of original text must be in the returned list, even if it is correct, in the order they appear in the original. The JSON should be a list of objects ("segments"), each with the following fields:

- text: The original text of the segment. Remove leading and trailing spaces, but keep any trailing newlines.
- corrections: A list of alternative corrections for that segment. Each correction should be a string.
- reason: A string explaining the reason for the correction.

A segment contains at least the word or words that need to be corrected, and should have only the minimum phrase containing those words. If the list of corrections in a segment is empty, the reason field should be an empty string. If two or more consecutive segments have no corrections, they should be grouped together into a single segment.
"""
    model = "gemini-2.5-pro-preview-03-25"
    model = "gemini-2.5-pro-preview-05-06"
    model = "gemini-2.5-pro-preview-06-05"
    generate_content_config = types.GenerateContentConfig(
        response_mime_type="text/plain",
        thinking_config=types.ThinkingConfig(include_thoughts=True),
        system_instruction=[
            types.Part.from_text(
                text=f"""Act as an expert in Esperanto. Consider every sentence in the following Esperanto passage. Find errors in grammar, awkward or inefficient phrasing, and misspellings, and suggest appropriate corrections. Make sure you also find any missing accusative endings, and ensure that the active participles are in the right tense. List only the problem words/phrases, their corrections, and the reason for the correction. Do not list any phrases which are already correct. Respond in English. Give also a final English translation for the passage.

{formatting}

Do not hallucinate references. Do not hallucinate a rule that a preposition takes an accusative of motion when it never does.

Remember that in Esperanto, when a preposition is used as a prefix to a verb, often the preposition is repeated, for example "eliris el la dormoĉambro" and "ĉirkaŭiron ĉirkaŭ la domo". Do not suggest that the preposition should be omitted in these cases.

Remember that in Esperanto, the "absolute participial construction" does not use a participle, but rather a verb, and the phrase would be introduced with "dum" (while). This is a phrase where the subject of the phrase is not the subject of the sentence. For example, in "The cat, eyes turning to the side, saw the dog," the subject of the phrase is "(the cat's) eyes", not "the cat". Thus, this sentence should be translated as "La kato, dum la okuloj turniĝis al la flanko, vidis la hundon." Do not suggest that the participle should be used in these cases. When the subject of the phrase is the same as the subject of the sentence, use a adverbial participle, for example: "La kato, turnante al la flanko, vidis la hundon." (The cat, [while] turning to the side, saw the dog.) When the participle describes the subject, then it is an adjectival participle, for example: "La kato turnanta al la flanko vidis la hundon." (The cat [which was] turning to the side saw the dog.)

Advice about prepositions and the accusative of motion: An accusative of motion is used with a preposition when the preposition indicates movement to a location, or when the preposition indicates a direction of movement. The accusative of motion is not used with a preposition when the preposition indicates a location. For example, "Mi piediras en la ĝardeno" means "I am walking within the garden" (within the bounds of the garden), while "Mi piediras en la ĝardenon" means "I am walking into the garden" (from outside to inside the garden). As another example "Mi piediras trans la rivero" means "I am walking across the river" (I'm currently located on the river), while "Mi piediras trans la riveron" means "I am walking across the river towards the other side of the river" (from one side of the river to the other side).

Specific advice about the preposition "tra": Normally "tra" does not take an accusative of motion, since it already implies motion. However, an accusative of motion may be used with "tra" to improve clarity if necessary. Such an accusative generally gives "tra" the meaning of "completely through and possibly beyond".

Specific advice about the preposition "ĉirkaŭ": "ĉirkaŭ" without an accusative of motion means "a location on all sides of something" or "a location on various sides of something". However, an accusative of motion is used with "ĉirkaŭ" to indicate movement to completely surround something, or to indicate movement to a location which one reaches by going around something.

Specific advice about the preposition "kontraŭ": "kontraŭ" usually means "against" or "opposite", in the physical or figurative sense of one thing facing another thing. For example: "Starigu la kandelabron kontraŭ la tablo." or "Ŝi sidis  kontraŭ la fajrejo." In cases where there is physical movement or turning in a new direction, "kontraŭ" is used with an accusative of motion to indicate the direction of the movement, for example: "Li levis la vizaĝon kontraŭ la plafonon". If something physically moves against something else, and reaches its goal, use the accusative of motion, for example: "ĵeti ŝtonon kontraŭ muron". In all other cases, do not use the accusative of motion with "kontraŭ".

Specific advice about the preposition "sur": It only takes the accusative when it indicates the destination of a movement. For example: "Mi metis la manon sur la tablon."

Specific advice about the preposition "trans": It only takes the accusative when it indicates movement to a location on the other side of something. For example: "La hirundo flugis trans la riveron."

Specific advice about the preposition "preter": It does not take the accusative, even for movement. For example: "Li pasis preter mi sen saluto." However, for movement, the accusative may be used only if it is necessary for clarity when not using the accusative would be unclear.

Advice about the prepositions "dum", "al", "post", and "el": They never take the accusative.

Advice about the verb "fari" and "igi": When it refers to making something to be something else, the object being made is in the accusative, but the object being made into is in the nominative. For example: "Mi faris/igis la infanon reĝo." (I made the child a king.), or "Ŝi faris/igis la domon ruĝa." (She made the house red.).

Advice about the accusative of proper names: The accusative of the name must end in "n" (or "-n" if the name doesn't end in a vowel). For example, for people named "Maria" and "Mustafa": "Maria salutis Mustafan", "Mustafa salutis Marian". For people whose name already ends in "n", for example, people named "Kalin" and "John": "Kalin salutis John-n", "John salutis Kalin-n". For people whose name ends in a consonant other than "n", for example people named "Karnak" and "Vos": "Karnak salutis Vos-n", "Vos salutis Karnak-n".

Occasionally you will see slashes (/) in the text. These slashes indicate italics.
"""
            ),
        ],
    )

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(
                    text="""“Je la nomo de Valkao, ne estu stultulo! Ĉu vi povas miri post ĉio, kion ni vidis? Ĉu vi ne vidas, ke tiuj estas veraj viroj ensorĉitaj de serpenthomo, kiu surhavas vian formon, kiel tiuj aliaj surhavis iliajn formojn? Nune vi estus mortigita kaj tiu tie monstro reĝus anstataŭ vi, nekonata de tiuj, kiuj genuis al vi. Saltu kaj mortigu rapide, alie ni estos finitaj. La Ruĝaj Mortigistoj, veraj viroj, proksime staras, kaj neniu krom vi povas atingi kaj mortigi lin. Rapidu!”

Kullo forskuis la alrapidantan vertiĝon, ĵetis sian kapon reen kun la malnova, defia gesto. Li longe, profunde enspiris kiel forta naĝisto antaŭ ol plonĝi en la maron; tiam, tirante la tapetojn reen, li atingis la podion per unu leosimila salto. Brule pravis. Tie staris viroj de la Ruĝaj Mortigistoj, gardistoj, kiuj estis trejnitaj por moviĝi tiel rapide kiel atakanta leopardo; iu ajn krom Kullo mortus antaŭ ol atingi la uzurpanton. Sed la vido de Kullo, identa kun la viro sur la podio, tute haltis ilin, dum iliaj mensoj momente estis stuporitaj, kaj tio estis sufiĉe. Tiu sur la podio moviĝis por tiri sian glavon, sed eĉ dum liaj fingroj ĉirkaŭfermis la glavtenilon, la glavo de Kullo elstaris malantaŭ liaj ŝultroj, kaj la aĵo, kiun viroj pensis esti la reĝo, falis antaŭen de la podio, kaj silente kuŝis sur la planko.

“Haltu!” La levita mano kaj reĝa voĉo de Kullo haltigis la impeton, kiu komenciĝis, kaj dum ili stuporite staris, li fingromontris al la aĵo, kiu kuŝis antaŭ ili—kies vizaĝo estis fadanta en tiun de serpento. Ili retiris sin, kaj el unu pordo venis Bruleo, kaj el alia venis Ka-nuo.

Tiuj ekprenis la sangan manon de la reĝo, kaj Ka-nuo diris: “Viroj de Valusio, vi vidis per viaj propraj okuloj. Ĉi tio estas la vera Kullo, la plej fortega reĝo, al kiu Valusio iam ajn genuis. La potenco de la Serpento estas rompita, kaj vi estas ĉiuj veraj viroj. Reĝo Kullo, kion vi ordonas?”

“Levu tiun putraĵon,” diris Kullo, kaj viroj el la gardantaro prenis la aĵon.

“Nun sekvu min,” diris la reĝo, kaj li iris al la Malbenita Ĉambro. Bruleo, kun rigardo de zorgo, ofertis subtenon per sia mano, sed Kullo forskuis lin.

La distanco ŝajnis senfina al la sangadanta reĝo, sed finfine li staris ĉe la pordo kaj feroce kaj malvarme ridis, kiam li aŭdis la hororigitajn eksklamojn de la konsilistoj.

Per liaj ordonoj, la gardistoj ĵetis la kadavron, kiun ili portis, apud la aliajn, kaj, gestante ĉiujn el la ĉambro, Kullo laste elpaŝis kaj fermis la pordon.

Ondo de vertiĝo lasis lin ŝancelitan. La vizaĝoj turnis sin al li, palaj, kaj mirinde kirliĝis kaj miksiĝis en fantoman nebulon. Li sentis la sangon de sia vundo rojeti laŭ siaj membroj, kaj li sciis, ke kion li estis faronta, li devis fari rapide, aŭ neniam.

Lia glavo raspiĝis el ĝia glavingo.

“Bruleo, ĉu vi ĉeestas?”

“Jes!” La vizaĝo de Bruleo rigardis lin tra la nebuleto, proksime al lia ŝultro, sed la voĉo de Bruleo sonis leŭgojn kaj epokojn for.

“Rememoru nian ĵuron, Bruleo. Kaj nun, petu ilin retropaŝi.”

Lia maldekstra brako liberigis spacon dum li eklevis sian glavon. Tiam, per tuta sia malfortiĝanta potenco, li trapuŝis ĝin tra la pordo en la framflankon, trapuŝante la grandan glavon ĝis la glavtenilo, kaj obturis la pordon por ĉiam.

Kun kruroj vaste stegantaj lin, li ebrie svingiĝis kaj turnis sin al la hororigitaj konsilistoj. “Ĉi tiu ĉambro estu duoble malbenita. Kaj tiuj putrantaj skeletoj kuŝu tie por ĉiam kiel signo de la mortanta forto de la serpento. Ĉi tie mi ĵuras, ke mi ĉasos la serpenthomojn de lando al lando, de maro al maro, donante neniun ripozon ĝis kiam ĉiu estos mortigita, boneco triumfos, kaj la potenco de la infero estos rompita. Ĉi tion mi ĵuras... mi... Kullo... reĝo... de... Valusio.”

Liaj kruroj malfortiĝis dum la vizaĝoj svingiĝis kaj kirliĝis. La konsilistoj saltis antaŭen, sed antaŭ ol ili povis atingi lin, Kullo falis sur la plankon, kaj senmove kuŝis, kun vizaĝo supren.

La konsilistoj rapidis ĉirkaŭ la falitan reĝon, parolante kaj kriante. Ka-nuo batis ilin reen per siaj fermitaj pugnoj, sovaĝe blasfemante.

“Reen, vi stultuloj! Ĉu vi volas subpremi la malmultan vivecon, kiu restas en li? Do, Bruleo, ĉu li mortas, aŭ ĉu li vivos?”—al la batalisto, kiu kliniĝis super la kolapsinta reĝo.

“Mortinta?” agacite rikanis Bruleo. “Tia viro kiel ĉi tiu ne estas tiel facile mortigita. Manko de somno kaj perdo de sango malfortigis lin—je Valkao, li havas dudek profundajn vundojn, sed neniu mortiga. Do, tiuj babilantaj stultuloj venigu la kortegajn virinojn ĉi tien tuj.”

La okuloj de Bruleo brilis per feroca, fiera lumo.

“Je Valkao, Ka-nuo, ĉi tie estas tia viro, kiun mi ne sciis ekzisti dum ĉi tiuj degeneritaj tagoj. Li rajdos sur selo post tre malmultaj tagoj, kaj tiam la serpenthomoj de la mondo gardu sin kontraŭ Kullo de Valusio. Je Valkao, tio estos rara ĉaso! Ah, mi antaŭvidas longajn jarojn de prospero por la mondo kun tia reĝo sur la trono de Valusio.”
"""
                ),
            ],
        ),
    ]

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        if chunk.text is not None:
            print(chunk.text, end="")


if __name__ == "__main__":
    generate()
