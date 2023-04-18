from app.modules.prompts.adapters import AdapterPromptsHistory


async def update_prompt_history(
    db_prompt_history: AdapterPromptsHistory, prompt_id: int, revision_id: int
):
    """
    Update prompt usage metric.
    """

    await db_prompt_history.create({"prompt_id": prompt_id, "revision_id": revision_id})
