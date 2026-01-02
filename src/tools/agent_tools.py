from livekit.agents import llm, function_tool


class Tools(llm.ToolContext):
    @function_tool(description="Lookup dosage or instructions for a medicine")
    def get_medicine_info(self, medicine_name: str) -> str:
        mock_db = {"paracetemol": "10 mg daily"}
        return mock_db.get(
            medicine_name.lower(), "No information found. Please Consult your doctor"
        )
