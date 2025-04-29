from pydantic_ai import Agent, RunContext
from models import Content, Presentation

def create_slide_gen_agent() -> Agent:
    
    slide_gen_agent = Agent(
        'google-gla:gemini-2.0-flash',
        deps_type=Content,
        result_type=Presentation,
        model_settings={"temperature": 0.0}
    )

    @slide_gen_agent.system_prompt
    def system_prompt(ctx: RunContext) -> str:
        return f"""
        You are assistant agent to help me generate slides for presentation.
        Use provided information {ctx.deps.content} about {ctx.deps.title} to summarize and synthesize content for the presentation.
        Given the following images information. Given each slide have size 1920x1080 px:
        IMAGES:
        """ + "\n".join(
            [f"{image.image_url}: {image.caption} have size {image.width}x{image.height}" for image in ctx.deps.images]
        ) + """
        Firstly, use given information to summarize and synthesize content for the presentation.
        The first slide is COVER, only include title of the presentation and subtitle.
        The last slide is CLOSING, only include "Thanks for watching".

        Secondly, select appropriate image for the slide. If there is no suitable image for the slide, simply return `None`.
        Finally, select the most appropriate layout for this slide, based on whether the slide has an image and its size.

        MUST USE `only text` for slides that do not have an image.
        USE `only image` for slides with large images.
        Make sure content is brief but clear and meaningful.

        Create between 10-20 slides.

        Return as Example:
        Attention is All You Need
        Presenter: Alex Chandler
        09-13-2022
        ---------------------
        Motivation
        ● Transformers were developed to solve the problem of machine
        translation and sequence transduction, or neural machine
        translation … but they do so much more!
        ○ Great performance in computer vision like ViT
        (Dosovitskiy, 2020)
        ○ Image Classification (CoCa Transformer)
        ○ Semantic Segmentation (ex: FD-SwinV2-G Transformer)
        ○ Object Detection (ex: FD-SwinV2-G Transformer)
        ---------------------
        Extended Readings
        Good Sources for Explainability:
        ● Blogs:
        ○ https://jinglescode.github.io/2020/05/27/illustrated-guide-transformer/
        ○ https://towardsdatascience.com/transformers-141e32e69591
        ○ https://jalammar.github.io/illustrated-transformer/
        ○ https://medium.com/analytics-vidhya/neural-machine-translation-using-bahdanau-attention-mechanism-d496c9be30c3
        ● Youtube:
        ○ https://www.youtube.com/watch?v=TQQlZhbC5ps
        Relevant Papers:
        ● Attention is All You Need: https://arxiv.org/abs/1706.03762
        ● BERT: https://arxiv.org/abs/1810.04805
        ● Roberta: https://arxiv.org/abs/1907.11692
        ● Swin Transformer: Hierarchical Vision Transformer using Shifted Windows: https://arxiv.org/abs/2103.14030
        ------------------
        Summary
        ● Transformers:
        ○ Dominate Everything
        ○ State of the art in Image Classification,
        Language Modeling, Speech Recognition,
        Vision Transformers (ex: ViT), Semantic
        Segmentation, Behavior / Decision Making, etc.
        """

    return slide_gen_agent
