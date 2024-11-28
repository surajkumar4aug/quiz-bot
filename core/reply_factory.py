
from .constants import BOT_WELCOME_MESSAGE, PYTHON_QUESTION_LIST


def generate_bot_responses(message, session):
    bot_responses = []

    current_question_id = session.get("current_question_id")
    if not current_question_id:
        bot_responses.append(BOT_WELCOME_MESSAGE)

    success, error = record_current_answer(message, current_question_id, session)

    if not success:
        return [error]

    next_question, next_question_id = get_next_question(current_question_id)

    if next_question:
        bot_responses.append(next_question)
    else:
        final_response = generate_final_response(session)
        bot_responses.append(final_response)

    session["current_question_id"] = next_question_id
    session.save()

    return bot_responses


def record_current_answer(answer, current_question_id, session):
    '''
    Validates and stores the answer for the current question in the session.
    '''
    try:
        if not current_question_id:
            raise ValueError("Invalid question ID.")

        if not isinstance(answer, str) or not answer.strip():
            raise ValueError("Answer must be a non-empty string.")

        if "answers" not in session:
            session["answers"] = {}

        # Store the answer in session
        session["answers"][current_question_id] = answer.strip()

        return True, ""

    except ValueError as e:
        return False, str(e)
    except KeyError as e:
        return False, f"Session error: {str(e)}"
    except Exception as e:
        return False, f"An unexpected error occurred: {str(e)}"


def get_next_question(current_question_id):
    '''
    Fetches the next question from the PYTHON_QUESTION_LIST based on the current_question_id.
    '''
    try:
        if current_question_id is None:
            return PYTHON_QUESTION_LIST[0]["question"], PYTHON_QUESTION_LIST[0]["id"]

        for idx, question in enumerate(PYTHON_QUESTION_LIST):
            if question["id"] == current_question_id:
                if idx + 1 < len(PYTHON_QUESTION_LIST):
                    return PYTHON_QUESTION_LIST[idx + 1]["question"], PYTHON_QUESTION_LIST[idx + 1]["id"]
                else:
                    raise IndexError("No more questions available.")
        raise ValueError("Invalid question ID.")
        
    except (IndexError, ValueError) as e:
        return None, str(e)
    except Exception as e:
        return None, f"An unexpected error occurred: {str(e)}"



def generate_final_response(session):
    '''
    Creates a final result message including a score based on the answers
    by the user for questions in the PYTHON_QUESTION_LIST.
    '''
    try:
        correct_answers = 0
        total_questions = len(PYTHON_QUESTION_LIST)
        user_answers = session.get("answers", {})

        if not isinstance(user_answers, dict):
            raise TypeError("Session 'answers' should be a dictionary.")

        for question in PYTHON_QUESTION_LIST:
            question_id = question["id"]
            correct_answer = question["answer"]
            user_answer = user_answers.get(question_id, "").strip().lower()

            if user_answer == correct_answer.strip().lower():
                correct_answers += 1

        score = f"You answered {correct_answers} out of {total_questions} questions correctly."
        return score

    except KeyError as e:
        return f"Data missing: {str(e)}"
    except TypeError as e:
        return f"Session error: {str(e)}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"
