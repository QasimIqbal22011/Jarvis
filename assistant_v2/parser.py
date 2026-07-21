import re


def parse_response(text):

    text = text.strip()

    # Only accept the first valid command
    match = re.search(
        r"(SAY|ASK|ACTION)\s*:\s*(.*)",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )

    if not match:
        return "SAY", None, text

    kind = match.group(1).upper()
    body = match.group(2).strip()


    if kind == "SAY":

        # Remove accidental extra commands
        body = re.split(
            r"\n(?:SAY|ASK|ACTION)\s*:",
            body,
            flags=re.IGNORECASE
        )[0]

        return "SAY", None, body.strip()



    if kind == "ASK":

        body = re.split(
            r"\n(?:SAY|ASK|ACTION)\s*:",
            body,
            flags=re.IGNORECASE
        )[0]

        return "ASK", None, body.strip()



    if kind == "ACTION":

        # take only first action line
        action_line = body.split("\n")[0].strip()

        if ":" not in action_line:

            return (
                "SAY",
                None,
                "Invalid action response."
            )


        tool, argument = action_line.split(
            ":",
            1
        )

        return (
            "ACTION",
            tool.strip(),
            argument.strip()
        )


    return "SAY", None, text