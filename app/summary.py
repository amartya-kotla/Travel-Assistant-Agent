from .utils import llm


def invoke_summary(context):

    context = str(context)

    SUMMARY_PROMPT = """

    You are an Itinerary Agent, your job is to take the context data given below and generate a Full itinerary highlighting the important points about
    travel, activities to do and commute. In the context data, you have 3 fields: transportation, activities and destination.

    This is the Context:
    {context}

    Provide the full itinerary in this format:

    TRAVEL:
    ----- travel details here --------

    THINGS TO DO:
    ------ activity details here ------
    """

    response = llm.invoke(SUMMARY_PROMPT.format(context=context))

    return response.content

