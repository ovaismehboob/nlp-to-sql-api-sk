import os
import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
#from plugins.ttsPlugin.ttsPlugin import TTSPlugin
#from plugins.sttPlugin.sttPlugin import STTPlugin
from dotenv import load_dotenv
import pyodbc
import time
import asyncio

from flask import Flask, request

app = Flask(__name__)



# Native functions are used to call the native skills
# 1. Create speech from the text
# 2. Create text from user's voice through microphone
def nativeFunctions(kernel, context, plugin_class,skill_name, function_name):
    native_plugin = kernel.import_skill(plugin_class, skill_name)
    function = native_plugin[function_name]
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = function.invoke(context=context)
        return result["result"]
    finally:
        loop.close()    
    return None

# Semantic functions are used to call the semantic skills
# 1. nlp_sql: Create SQL query from the user's query
def semanticFunctions(kernel, skills_directory, skill_name, input):
    functions = kernel.import_semantic_plugin_from_directory(skills_directory, "plugins")
    summarizeFunction = functions[skill_name]
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = summarizeFunction(input)
    finally:
        loop.close()
    return result

# Function to get the result from the database
def get_result_from_database(sql_query):
    server_name = os.environ.get("server_name")
    database_name = os.environ.get("database_name")
    username = os.environ.get("SQLADMIN_USER")
    password = os.environ.get("SQL_PASSWORD")
    print("Server name is "+ server_name)
    print("Database name is "+ server_name)
    print("Username is "+ username)
    print("Password is "+ password)
    
    conn = pyodbc.connect('DRIVER={driver};SERVER={server_name};DATABASE={database_name};UID={username};PWD={password};timeout=120;query timeout=120'.format(driver="ODBC Driver 17 for SQL Server",server_name=server_name, database_name=database_name, username=username, password=password))
    
    cursor = conn.cursor()
    try:
        cursor.execute(sql_query)
        result = cursor.fetchone()
    except:
        return "No Result Found"
    cursor.close()                                                                                                      
    conn.close()
    return result[0]
app = Flask(__name__)

@app.route("/")
def health():
    openaiendpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    return "Service is running and the Azure OpenAI endpoint is "+ openaiendpoint

@app.route("/query", methods=['POST'])
async def handle_query():
    #Load environment variables from .env file
    #Commented out for container 
    #load_dotenv()

    # Get JSON data from the request
    data = request.get_json()

    # Get the 'query' value from the data
    query = data['query']

    #query = request.form.get('query')

       # Create a new kernel
    kernel = sk.Kernel()
    context = kernel.create_new_context()
    context['result'] = ""

    # Configure AI service used by the kernel
    #deployment, api_key, endpoint = sk.azure_openai_settings_from_dot_env()


    # Read from environment variables 
    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME")
    api_key = os.environ.get("AZURE_OPENAI_API_KEY")
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")


    # Add the AI service to the kernel
    kernel.add_text_completion_service("dv", AzureChatCompletion(deployment_name=deployment, endpoint=endpoint, api_key=api_key))

    skills_directory = "."
    sql_query = await semanticFunctions(kernel, skills_directory, "nlpToSQLPlugin", query)
    sql_query = sql_query.result.split(';')[0]
    print("The SQL query is: {}".format(sql_query))

    # Use the query to call the database and get the output
    result = get_result_from_database(sql_query)

  
    # Now you can use the 'query' variable in your function

    return "Response: " + str(result);


#if __name__ == "__main__":

app.run(host='0.0.0.0', port=5000)