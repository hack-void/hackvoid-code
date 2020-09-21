import re
import json
import argparse
import time


# Remove all newlines and white-spaces
def deconstruct_code(code):
    code = re.sub(' *', '', code)
    return code.split('\n')

# Global variable for complete compiled html code
complete_html = []

# Function for compiling .hv files
def compile(decon_hv_code):

    # Variable for runtime block ending saves
    block_ends = []
    for unit in decon_code:

        # If white-space, newline or comment detected
        if unit == '' or unit == '\n' or unit[0:2] == '//':
            # Ignore
            continue

        # If end-of-block detected
        if unit[0] == '}':
            # Pop the latest block end from the stack and add it to the complete html code
            complete_html.append(block_ends.pop())
            continue

        # If start of the block detected
        if unit[-1] == '{':
            # Parse the block name
            block_name = re.findall('^[a-z]*\[', unit)[0]
            block_name = re.sub('\[', '', block_name)

            # Parse the block attributes
            block_attrs = re.findall('\[\{.*\}\]', unit)[0]
            block_attrs = re.sub('(\[|\])', '', block_attrs)
            block_attrs = json.loads(block_attrs)
            block_attrs_string = ""

            # Join it all in a string
            for i in block_attrs:
                block_attrs_string += f'{i}="{block_attrs[i]}" '

            # Remove the end white-space
            block_attrs_string = block_attrs_string[0:-1]

            # If no attributes are passed, don't add it. Else - add the attr field
            if not block_attrs_string == '':
                complete_html.append(f"<{block_name} {block_attrs_string}>\n")
            else:
                complete_html.append(f"<{block_name}>\n")

            # Add the ending of the block to the stack
            block_ends.append(f'</{block_name}>\n')
            continue


        # If oneliner detected
        if re.match('[a-zA-Z0-9].*\](\{.*\}|)', unit) or unit[0] == '"' and unit[-1] == '"':
            
            # Check, if regular text has been passed in
            if unit[0] == '"' and unit[-1] == '"':
                text = re.findall('".*"', unit)[0]
                complete_html.append(text + '\n')
                continue

            # Parse the block name
            block_name = re.findall('^[a-z]*\[', unit)[0]
            block_name = re.sub('\[', '', block_name)

            # Parse the block attributes
            block_attrs = re.findall('\[\{.*\}\]', unit)[0]
            block_attrs = re.sub('(\[|\])', '', block_attrs)
            block_attrs = json.loads(block_attrs)
            block_attrs_string = ""

            # Join it all in a string
            for i in block_attrs:
                block_attrs_string += f'{i}="{block_attrs[i]}" '

            # Remove the end white-space
            block_attrs_string = block_attrs_string[0:-1]

            # Parse content
            content = re.findall('\]\{".*\}$', unit)

            # If content exists, add it. Else - dont add the field
            if content:
                block_content = re.sub('(\]|\{|\}|")', '', content[0])

                # If no attributes are passed, don't add it. Else - add the attr field
                if not block_attrs_string == '':
                    complete_html.append(f'<{block_name} {block_attrs_string}>{block_content}</{block_name}>\n')
                else:
                    complete_html.append(f'<{block_name}>{block_content}</{block_name}>\n')

                continue
            
            # If no attributes are passed, don't add it. Else - add the attr field
            if unit[-1] == ']':
                if not block_attrs_string == '':
                    complete_html.append(f'<{block_name} {block_attrs_string}>\n')
                else:
                    complete_html.append(f'<{block_name}>\n')
                continue
        
        # If there are no rule, that can catch the unit, throw a message and continue parsing.
        print(f"!![COMPILE_ERROR]: Unit '{unit}' cannot be compiled!")
        continue


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('INPUT', metavar='INPUT', type=str,
                    help='Path to .hv file (source code)')
    parser.add_argument('OUTPUT', metavar='OUTPUT', type=str,
                    help='Path and name of the output file')
    args = parser.parse_args()

    start_time = time.time()
    with open(args.INPUT, 'r') as f:
        raw_code = f.read()
    decon_code = deconstruct_code(raw_code)
    #print(decon_code)
    compile(decon_code)
    with open(args.OUTPUT, 'w') as f:
        f.writelines(complete_html)
    print("Done!")
    print(f"========= {time.time() - start_time} seconds =========")
