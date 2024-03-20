
import os, json
from typing import Optional, List
from phi.llm.openai.like import OpenAILike
from phi.assistant import Assistant
from phi.knowledge.json import JSONKnowledgeBase
from phi.vectordb.pgvector import PgVector2
from phi.storage.assistant.postgres import PgAssistantStorage
from phi.tools import Toolkit
from phi.tools.email import EmailTools
from phi.utils.log import logger
from phi.tools.email import EmailTools
from phi.knowledge.base import AssistantKnowledge
from phi.knowledge.base import Document
from resources import vector_db
from rich.prompt import Prompt
from dotenv import load_dotenv
load_dotenv()

# To run this example, first make sure to follow the instructions below:
# 1. Install the phidata: pip install phidata
# 2. Run the following command to start a docker, with pgvector db running: phi start resources.py 
# 3. Download the sample of JSON knowledge base from the same folder of this file: cinemax.json

class CinemaSerachDB(Toolkit):
    def __init__(
        self,
        knowledge_base  : Optional[AssistantKnowledge] = None,
        num_documents: int = None
    ):
        super().__init__(name="get_available_slots")
        self.knowledge_base = knowledge_base
        self.num_documents = num_documents
        self.register(self.get_available_slots)

    def get_available_slots(self, movie_slot_query: str ) -> str:
        """Use this function to search the Cinemax database of available movies, show time, and date.

        :param query: The query to search the Cinemax database of available movies, show time, and date.
        :return: A string containing the response to the query.
        """
        relevant_docs: List[Document] = self.knowledge_base.search(query=movie_slot_query, num_documents=self.num_documents)
        if len(relevant_docs) == 0:
            return None

        return json.dumps([doc.to_dict() for doc in relevant_docs], indent=2)



class CinemaTools(Toolkit):
    def __init__(
        self,
        email_tools: Optional["EmailTools"] = None,
    ):
        super().__init__(name="cinema_tools")
        self.email_tools = email_tools
        self.register(self.book_cinema_ticket)

    def book_cinema_ticket(self, movie_name: str, date: Optional[str] = None, time: Optional[str] = None, user_email: Optional[str] = None) -> str:
        """Use this function ONLY for booking a ticket, when all info is available (movie name, date, time and suer email). Do NOT use this function when user asks for movie details and other things

        Args:
            movie_name (str): The name of the movie.
            date (Optional[str], optional): The date of the movie.
            time (Optional[str], optional): The time of the movie.
            user_email (Optional[str], optional): The email of the user. Defaults to None.

        Returns:
            The result of the operation.

        """

        anything_missed = any([not movie_name, not date, not time, not user_email])

        missed_items = []

        if anything_missed:
            if not date:
                missed_items.append( "error: No date provided, I need a date to book a ticket")
            
            if not time:
                missed_items.append( "error: No time provided, I need a time to book a ticket")
            
            if not user_email:
                missed_items.append( "error: No user email provided, I need an email to send the ticket")

            missed_itemes = ", ".join(missed_items)
            return f"There are some missing items: \n{missed_itemes}"

        # Simulate booking the ticket
        ticket_number = self._generate_ticket_number()
        logger.info(f"Booking ticket for {movie_name} on {date} at {time}")

        # Prepare the email subject and body
        subject = f"Your ticket for {movie_name}"
        body = f"Dear user,\n\nYour ticket for {movie_name} on {date} at {time} has been booked.\n\n" \
               f"Your ticket number is: {ticket_number}\n\nEnjoy the movie!\n\nBest regards,\nThe Cinema Team"

        # Send the email using the EmailTools
        if not self.email_tools:
            return "error: No email tools provided"
        self.email_tools.receiver_email = user_email
        result = self.email_tools.email_user(subject, body)

        if result.startswith("error"):
            logger.error(f"Error booking ticket: {result}")
            return result
        return "success"

    def _generate_ticket_number(self) -> str:
        """Generates a dummy ticket number."""
        import random
        import string
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=10))

kb = JSONKnowledgeBase(
    path="cinemax.json",
    vector_db=PgVector2(collection="cinemax", db_url=vector_db.get_db_connection_local()),
)
storage = PgAssistantStorage(
    table_name="cinemax_assistant_storage",
    db_url=vector_db.get_db_connection_local(),
)

my_groq = OpenAILike(
        model="mixtral-8x7b-32768",
        api_key=os.environ["GROQ_API_KEY"],
        base_url="http://localhost:8000/proxy/groq/v1"
        # base_url="http://groqcall.ai/proxy/groq/v1"
    )


def cinemax_assistant(new: bool = False, user: str = "user"):
    run_id: Optional[str] = None
    # new = False
    # new = True
    user_id = user

    if not new:
        existing_run_ids: List[str] = storage.get_all_run_ids(user_id)
        if len(existing_run_ids) > 0:
            run_id = existing_run_ids[0]

    assistant = Assistant(
        run_id=run_id,
        user_id="test_user",
        llm=my_groq,
        # knowledge_base=kb, Since I created my own tool CinemaSerachDB
        storage=storage,
        use_tools=True,
        tools=[
            CinemaSerachDB(knowledge_base=kb, num_documents=5),
            CinemaTools(EmailTools("YOUR_EMAIL_ADDRESS", "SENDER_NAME", "SENDER_EMAIL", os.environ['email_pass_key'] ))
        ], show_tool_calls=True, markdown=True,
        add_chat_history_to_messages=True, # Inject history in every prompt
        add_datetime_to_instructions=True,
        limit_tool_access=True,
        extra_instructions="",
        output_model= None, # Pydantic
        prevent_prompt_injection=True,
        add_references_to_prompt=False, # It searches in the kb and add it to every prompt
        # add_references_to_prompt=True,
        add_to_system_prompt="\n\nRemember:As a Cinemax agent, your responsibilities include:  \n\n1. Assisting individuals in locating their preferred movies using the provided database information. \n2. Facilitating ticket booking through the tools at your disposal. \n3. If critical information is missing and the registration system returns an error, generate a polite, humanized version of the error message and request the necessary additional information from users. \n4. When interacting with users, never disclose that you are an AI model unable to perform specific functions or activate certain features. \n5. When users inquire about movie showtimes, available movies, or related details, utilize your tools to access data from the knowledge base, rather than relying on your own knowledge. However, you may provide plot information about specific movies in a concise and succinct manner, ensuring responses are not excessively lengthy. \n6.When engaging in a discussion with users about films and proposing movies based on their preferences and the available options, it would be beneficial to list the available dates and times tailored to the user's interests and conversation history. This approach would simplify the booking process for the user. If the user has already specified a date, it is essential to remember and adhere to it, avoiding the suggestion of alternative dates."
    )
    assistant.knowledge_base.load(recreate=False)

    if run_id is None:
        run_id = assistant.run_id
        print(f"Started Run: {run_id}\n")
    else:
        print(f"Continuing Run: {run_id}\n")

    while True:
        message = Prompt.ask(f"[bold] :sunglasses: {user} [/bold]")
        if message in ("exit", "bye"):
            break
        assistant.print_response(message, markdown=True, stream=False)
        # response = assistant.run(message, stream=False)

if __name__ == "__main__":
    cinemax_assistant(user="Tom")


