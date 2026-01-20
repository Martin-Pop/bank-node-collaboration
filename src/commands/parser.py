def parse_command(message: str):
    """
    Parses command, splits by spaces
    :param message: provided command
    :return: code and args
    """
    parts = message.strip().split()
    if not parts:
        return 'ER', []

    return parts[0].strip().upper(), parts[1:]

def parse_address(message: str):
    """
    Parses address in this format <account_number>/<ip>
    :param message: address to parse
    :return: if it has invalid format, returns None
    """
    parts = message.strip().split('/')
    if len(parts) == 2:
        return parts[0].strip(), parts[1].strip()
    return None, None

def is_command_for_us(our_bank_code: str, message: str):
    """
    Determines if command is for our bank to handle by parsing the client account number which contains bank address.
    :param our_bank_code: our bank code to compare it with
    :param message: message to parse
    :return: True if command it for us (our bank code or invalid format / command does not contain bank address)
    """
    if not message: return True
    account, bank_code = parse_address(message)
    if account and bank_code:
        if bank_code == our_bank_code:
            return True
        return False
    return True


