def parse_command(message: str):
    parts = message.strip().split()
    if not parts:
        return 'ER', []

    return parts[0].strip().upper(), parts[1:]

def parse_address(message: str):
    parts = message.strip().split('/')
    if len(parts) == 2:
        return parts[0].strip(), parts[1].strip()
    return None, None

def is_command_for_us(our_bank_code: str, message: str):
    if not message: return True
    account, bank_code = parse_address(message)
    if account and bank_code:
        if bank_code == our_bank_code:
            return True
        return False
    return True


