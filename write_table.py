import codecs

INVALID_UTF8_CHARS = [0xC0, 0xC1, 0xF5, 0xF6, 0xF7, 0xF8, 0xF9, 0xFA, 0xFB, 0xFC, 0xFD, 0xFE, 0xFF]

def is_valid_utf8(hex_sequence):
    try:
        return codecs.decode(hex_sequence, "hex").decode('utf-8')
    except:
        return None

def is_start_of_multi_byte(hex_sequence):
    if len(hex_sequence) > 6:
        return False
    # Nasty brute force
    for b in range(0x00, 0xFF):
        if b in INVALID_UTF8_CHARS:
            continue
        if is_valid_utf8(hex_sequence + f'{b:02X}'):
            return True
        if is_start_of_multi_byte(hex_sequence + f'{b:02X}'):
            return True
    return False

def generate_html_table(lead_bytes=''):
    print(f"Generating HTML table with offset {'00' if lead_bytes=='' else lead_bytes}")
    html = f"<html><head><title>UTF-8 Byte Table: offset {lead_bytes}</title></head><style>td.invalid {{background-color: grey;}}</style></head><body>"
    html += f"<h1>Offset {'__' if lead_bytes=='' else lead_bytes} + </h1><table border='1'>"

    # Header row
    html += "<tr><th></th>"
    for col in range(0x00, 0x10):
        html += f"<th>0x{col:02X}</th>"
    html += "</tr>"

    # Data rows
    for row in range(0x00, 0xF1, 0x10):
        html += f"<tr><th>0x{row:02X}</th>"
        for col in range(0x00, 0x10):
            hex_string = lead_bytes + f'{row + col:02X}'
            utf_char = is_valid_utf8(hex_string)
            # TODO: why???
            if utf_char=='\x80':
                utf_char = '€'
            if utf_char:
                html += f"<td>{utf_char}</td>"
            elif is_start_of_multi_byte(hex_string):
                html += f'<td><a href="utf8_{hex_string}.html">{row + col:02X}</a></td>'
                # Recursively write the linked table
                html_content = generate_html_table(hex_string)
                with open(f"utf8_{hex_string}.html", "w", encoding="utf-8") as file:
                    file.write(html_content)
            else:
                html += f'<td class="invalid"></td>'
        html += "</tr>"

    html += "</table></body></html>"
    return html

# Write the HTML to a file
html_content = generate_html_table()
with open(f"utf8_00.html", "w") as file:
    file.write(html_content)

