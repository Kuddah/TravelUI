"""Chain that makes API calls and summarizes the responses to answer a question."""
from __future__ import annotations

from typing import Any, Dict, List, Optional
import json
from pydantic import Field, root_validator

from langchain.base_language import BaseLanguageModel
from langchain.callbacks.manager import (
    AsyncCallbackManagerForChainRun,
    CallbackManagerForChainRun,
)
import sqlite3
import isodate
from datetime import datetime
from prompt import API_RESPONSE_PROMPT, API_URL_PROMPT
from langchain.chains.base import Chain
from langchain.chains.llm import LLMChain
from langchain.prompts import BasePromptTemplate
from langchain.requests import TextRequestsWrapper


class APIChain(Chain):
    """Chain that makes API calls and summarizes the responses to answer a question."""

    api_request_chain: LLMChain
    api_answer_chain: LLMChain
    requests_wrapper: TextRequestsWrapper = Field(exclude=True)
    api_docs: str
    question_key: str = "question"  #: :meta private:
    output_key: str = "output"  #: :meta private:

    @property
    def input_keys(self) -> List[str]:
        """Expect input key.

        :meta private:
        """
        return [self.question_key]

    @property
    def output_keys(self) -> List[str]:
        """Expect output key.

        :meta private:
        """
        return [self.output_key]

    @root_validator(pre=True)
    def validate_api_request_prompt(cls, values: Dict) -> Dict:
        """Check that api request prompt expects the right variables."""
        input_vars = values["api_request_chain"].prompt.input_variables
        expected_vars = {"question", "api_docs"}
        if set(input_vars) != expected_vars:
            raise ValueError(
                f"Input variables should be {expected_vars}, got {input_vars}"
            )
        return values

    @root_validator(pre=True)
    def validate_api_answer_prompt(cls, values: Dict) -> Dict:
        """Check that api answer prompt expects the right variables."""
        input_vars = values["api_answer_chain"].prompt.input_variables
        expected_vars = {"question", "api_docs", "api_url", "api_response"}
        if set(input_vars) != expected_vars:
            raise ValueError(
                f"Input variables should be {expected_vars}, got {input_vars}"
            )
        return values

    def _call(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, str]:
        _run_manager = run_manager or CallbackManagerForChainRun.get_noop_manager()
        question = inputs[self.question_key]
        api_url = self.api_request_chain.predict(
            question=question,
            api_docs=self.api_docs,
            callbacks=_run_manager.get_child(),
        )
        _run_manager.on_text(api_url, color="green", end="\n", verbose=self.verbose)
        api_response = self.requests_wrapper.get(api_url)
        api_response1 = json.loads(api_response)
                # Connect to the SQLite database file (this will create the file if it doesn't exist)
        conn = sqlite3.connect('flights.db')
        cursor = conn.cursor()

        # Create tables
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS FlightOffers (
            id TEXT PRIMARY KEY,
            price REAL,
            currency TEXT,
            layover_duration TEXT,
            duration TEXT,
            total_stops INTEGER,
            origin_departure_time TEXT,
            destination_arrival_time TEXT,
            layovers TEXT
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS FlightSegments (
            id INTEGER PRIMARY KEY,
            flight_offer_id INTEGER,
            airline TEXT,
            flight_number TEXT,
            departure_time TEXT,
            arrival_time TEXT,
            aircraft_type TEXT,
            operating_carrier TEXT,
            departure_city TEXT,
            arrival_city TEXT,
            terminal_departure TEXT,
            terminal_arrival TEXT,
            FOREIGN KEY (flight_offer_id) REFERENCES FlightOffers (id)
        )
        ''')
        print(api_response1)  # Add this line before the line that raises the KeyError


        for flight_offer in api_response1["data"]:
            # Calculate the layover duration
            duration = isodate.parse_duration(flight_offer['itineraries'][0]['duration'])
            arrival_time_at = datetime.fromisoformat(flight_offer['itineraries'][0]['segments'][0]['arrival']['at'])
            if len(flight_offer['itineraries'][0]['segments']) > 1:
                departure_time_from = datetime.fromisoformat(flight_offer['itineraries'][0]['segments'][1]['departure']['at'])
            else:
                departure_time_from = None

                # Get the origin departure time and destination arrival time
            origin_departure_time = flight_offer['itineraries'][0]['segments'][0]['departure']['at']
            destination_arrival_time = flight_offer['itineraries'][0]['segments'][-1]['arrival']['at']
            if departure_time_from is not None:
                layover_duration = departure_time_from - arrival_time_at
            else:
                layover_duration = None


        # Get the list of layovers as a string
            layovers = ', '.join([segment['arrival']['iataCode'] for segment in flight_offer['itineraries'][0]['segments'][:-1]])

            # Insert the flight offer into the FlightOffers table
            cursor.execute('''
                INSERT OR REPLACE INTO FlightOffers (price, currency, layover_duration, duration, total_stops, layovers, id, origin_departure_time, destination_arrival_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                flight_offer['price']['total'],
                flight_offer['price']['currency'],
                str(layover_duration),
                str(duration),
                len(flight_offer['itineraries'][0]['segments']) - 1,
                layovers,
                flight_offer['id'],
                origin_departure_time,
                destination_arrival_time
            ))

            flight_offer_id = flight_offer['id']
            # Iterate through the itineraries in the flight offer
            for itinerary in flight_offer['itineraries']:
                # Insert the flight segments into the FlightSegments table
                for segment in itinerary['segments']:
                    cursor.execute('''
                        INSERT OR REPLACE INTO FlightSegments (
                            flight_offer_id,
                            airline,
                            flight_number,
                            departure_time,
                            arrival_time,
                            aircraft_type,
                            operating_carrier,
                            departure_city,
                            arrival_city,
                            terminal_departure,
                            terminal_arrival
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        flight_offer_id,
                        segment['carrierCode'],
                        segment['number'],
                        segment['departure']['at'],
                        segment['arrival']['at'],
                        segment['aircraft']['code'],
                        segment['operating']['carrierCode'],
                        segment['departure']['iataCode'],
                        segment['arrival']['iataCode'],
                        segment['departure'].get('terminal', ''),
                        segment['arrival'].get('terminal', '')
                    ))

        # Commit the changes and close the connection
        conn.commit()
        
        # ... (previous code)

        # Convert the api_response object to a string
        api_response_str = json.dumps(api_response1)
        print (api_response_str)
        # Check if the number of tokens in the api_response_str is more than 4000
        if len(api_response_str.split()) > 4000:
            # Query all the data in the FlightOffers table
            cursor.execute("SELECT * FROM FlightOffers")
            flight_offers_data = cursor.fetchall()

            # Create a new dictionary containing the queried data
            sql_response = {"data": flight_offers_data}
            print (sql_response)
            # Use sql_response instead of api_response
            _run_manager.on_text(
                sql_response, color="yellow", end="\n", verbose=self.verbose
            )
            answer = self.api_answer_chain.predict(
                question=question,
                api_docs=self.api_docs,
                api_url=api_url,
                api_response=sql_response,
                callbacks=_run_manager.get_child(),
            )
        else:
            _run_manager.on_text(
                api_response, color="yellow", end="\n", verbose=self.verbose
            )
            answer = self.api_answer_chain.predict(
                question=question,
                api_docs=self.api_docs,
                api_url=api_url,
                api_response=api_response,
                callbacks=_run_manager.get_child(),
            )
        conn.commit()
        conn.close()
        return {self.output_key: answer}


    async def _acall(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[AsyncCallbackManagerForChainRun] = None,
    ) -> Dict[str, str]:
        _run_manager = run_manager or AsyncCallbackManagerForChainRun.get_noop_manager()
        question = inputs[self.question_key]
        api_url = await self.api_request_chain.apredict(
            question=question,
            api_docs=self.api_docs,
            callbacks=_run_manager.get_child(),
        )
        await _run_manager.on_text(
            api_url, color="green", end="\n", verbose=self.verbose
        )
        api_response = await self.requests_wrapper.aget(api_url)
        await _run_manager.on_text(
            api_response, color="yellow", end="\n", verbose=self.verbose
        )
        answer = await self.api_answer_chain.apredict(
            question=question,
            api_docs=self.api_docs,
            api_url=api_url,
            api_response=api_response,
            callbacks=_run_manager.get_child(),
        )
        return {self.output_key: answer}

    @classmethod
    def from_llm_and_api_docs(
        cls,
        llm: BaseLanguageModel,
        api_docs: str,
        headers: Optional[dict] = None,
        api_url_prompt: BasePromptTemplate = API_URL_PROMPT,
        api_response_prompt: BasePromptTemplate = API_RESPONSE_PROMPT,
        **kwargs: Any,
    ) -> APIChain:
        """Load chain from just an LLM and the api docs."""
        get_request_chain = LLMChain(llm=llm, prompt=api_url_prompt)
        requests_wrapper = TextRequestsWrapper(headers=headers)
        get_answer_chain = LLMChain(llm=llm, prompt=api_response_prompt)
        return cls(
            api_request_chain=get_request_chain,
            api_answer_chain=get_answer_chain,
            requests_wrapper=requests_wrapper,
            api_docs=api_docs,
            **kwargs,
        )

    @property
    def _chain_type(self) -> str:
        return "api_chain"
