from langchain.prompts import PromptTemplate


class FashionRecommenderAgent:
    def __init__(self, llm):
        self.llm = llm
        self.prompt = self._get_prompt()
        self.chain = self._get_chain()

    def _get_prompt_template(self):
        template = (
            "You are a fashion recommender for H&M.\n"
            "\n"
            "Customer request: {user_input}\n"
            "\n"
            "Gender: {gender}\n"
            "\n"
            "Generate 3-5 necessary fashion items with detailed descriptions,"
            " tailored for an H&M-style dataset and appropriate for the specified gender.\n" 
            "Each item description should be specific, suitable for creating embeddings, and relevant to the gender.\n"
            "\n"
            "STRICTLY FOLLOW the next response format:\n"
            "<emoji> <item 1 category> @ <item 1 description> | <emoji> <item 2 category> @ <item 2 description> | <emoji> <item 3 category> @ <item 3 description> | <Additional items if necessary> | <BRIEF OUTFIT SUMMARY AND STYLING TIPS WITH EMOJIS>"
            "\n"
            "Example for male gender:\n"
            "👖 Pants @ Slim-fit dark wash jeans with subtle distressing | 👕 Top @ Classic white cotton polo shirt with embroidered logo | 👟 Footwear @ Navy canvas sneakers with white soles | 🧥 Outerwear @ Lightweight olive green bomber jacket | 🕶️👔 Versatile casual look! Mix and match for various occasions. Add accessories for personal flair! 💼⌚\n"
            "\n"
            "Example for female gender:\n"
            "👗 Dress @ Floral print wrap dress with flutter sleeves | 👠 Footwear @ Strappy nude block heel sandals | 👜 Accessory @ Woven straw tote bag with leather handles | 🧥 Outerwear @ Cropped denim jacket with raw hem | 🌸👒 Perfect for a summer day out! Layer with the jacket for cooler evenings. Add a wide-brim hat for extra style! 💃🏻🕶️\n"
            "\n"
            "Ensure each item category has a relevant emoji, each item description is detailed, unique, and appropriate for the specified gender.\n"
            "Make sure to take into account the gender when selecting items and descriptions.\n"
            "Make sure that you strictly follow the provided response format.\n"
            "Don't forget to generate outfit summary at the end with a proper separation as shown in the example.\n"
        )
        return template
    
    def _get_prompt(self):
        template = self._get_prompt_template()

        prompt = PromptTemplate(
            input_variables=["user_input", "gender"],
            template=template,
        )

        return prompt

    def _get_chain(self):
        return self.prompt | self.llm
    
    def get_fashion_recommendations(self, user_input, gender):
        response = self.chain.invoke({"user_input": user_input, "gender": gender})
        items = response.content.strip().split(" | ")

        outfit_summary = items[-1] if len(items) > 1 else "No summary available."
        item_descriptions = items[:-1] if len(items) > 1 else items
        
        parsed_items = []
        for item in item_descriptions:
            try:
                emoji_category, description = item.split(" @ ", 1)
                emoji, category = emoji_category.split(" ", 1)
                parsed_items.append((emoji, category, description))
            except ValueError:
                parsed_items.append(("🔷", "Item", item))
        
        return parsed_items, outfit_summary