# I. Before release 

## A. Initial update / migration Data check

Before testing, set-up the following in the old version to make sure that we can see the data is properly migrated:
- [x] Changing appearance / theme to something that is obviously different from default set-up 🔥
- [x] Ensure there are a few chat threads 🔥🔥🔥
- [x] Ensure there are a few favourites / star threads 🔥🔥🔥
- [x] Ensure there are 2 model downloaded 🔥🔥
- [x] Ensure there are 2 import on local provider (llama.cpp) 
- [x] Modify MCP servers list and add some ENV value to MCP servers
- [x] Modify Local API Server 🔥
- [x] HTTPS proxy config value 🔥
- [x] Add 2 custom assistants to Jan 🔥🔥
- [x] Create a new chat with the custom assistant 🔥🔥🔥
- [x] Change the `App Data` to some other folder
- [x] Create a Custom Provider 🔥🔥 (Not verified yet)
- [x] Disabled some model providers 🔥🔥🔥
#### Validate that the update does not corrupt existing user data or settings (before and after update show the same information):
- [x] Threads
	- [x] Previously used model and assistants is shown correctly
	- [x] Can resume chat in threads with the previous context
- [x] Assistants
- Settings:
	- [x] Appearance
	- [x] MCP Servers 
	- [x] Local API Server
	- [x] HTTPS Proxy
- [x] Custom Provider Set-up

#### In `Hub`:
- [x] Can see model from HF listed properly ✅
- [x] Downloaded model will show `Use` instead of `Download` ✅
- [x] Toggling on `Downloaded` on the right corner show the correct list of downloaded models 🔥🔥

#### In `Settings -> General`:
- [x] Ensure the `App Data` path is the same ✅ 
- [x] Click Open Logs, App Log will show ✅
	
#### In `Settings -> Model Providers`:
- [x] Llama.cpp still listed downloaded models and user can chat with the models 🔥🔥🔥
- [x] Llama.cpp still listed imported models and user can chat with the models 
- [x] Remote model still retain previously set up API keys and user can chat with model from the provider without having to re-enter API keys
- [x] Enabled and Disabled Model Providers stay the same as before update 🔥

#### In `Settings -> Extensions`, check that following exists: ✅
- [x] Conversational ✅ 
- [x] Jan Assistant ✅
- [x] Download Manager ✅ 
- [x] llama.cpp Inference Engine ✅

## B. `Settings` 

#### In `General`:
- [x] Ensure `Community` links work and point to the correct website 🔥🔥 (Scrolldown problem)
- [x] Ensure the `Check for Updates` function detect the correct latest version ✅
- [ ] [ENG] Create a folder with un-standard character as title (e.g. Chinese character) => change the `App data` location to that folder => test that model is still able to load and run properly.
#### In `Appearance`:
- [x] Toggle between different `Theme` options to check that they change accordingly and that all elements of the UI are legible with the right contrast:
	- [x] Light 🔥
	- [x] Dark 🔥
	- [x] System (should follow your OS system settings) 🔥
- [x] Change the following values => close the application => re-open the application => ensure that the change is persisted across session:
	- [x] Theme 🔥
	- [x] Font Size 🔥
	- [x] Window Background 🔥
	- [x] App Main View 🔥
	- [x] Primary 🔥
	- [x] Accent 🔥
	- [x] Destructive 🔥
	- [x] Chat Width 🔥
		- [x] Ensure that when this value is changed, there is no broken UI caused by it 🔥
	- [x] Code Block 🔥
	- [x] Show Line Numbers 🔥
- [ENG] Ensure that when click on `Reset` in the `Appearance` section, it reset back to the default values 🔥🔥
- [ENG] Ensure that when click on `Reset` in the `Code Block` section, it reset back to the default values 🔥🔥

#### In `Model Providers`:

In `Llama.cpp`:
- [x] After downloading a model from hub, the model is listed with the correct name under `Models` 🔥🔥🔥
- [x] Can import `gguf` model with no error
- [x] Imported model will be listed with correct name under the `Models`
- [x] Check that when click `delete` the model will be removed from the list 🔥🔥
- [x] Deleted model doesn't appear in the selectable models section in chat input (even in old threads that use the model previously)
- [x] Ensure that user can re-import deleted imported models
- [x] Enable `Auto-Unload Old Models`, and ensure that only one model can run / start at a time. If there are two model running at the time of enable, both of them will be stopped. 
- [x] Disable `Auto-Unload Old Models`, and ensure that multiple models can run at the same time.
- [x] Enable  `Context Shift` and ensure that context can run for long without encountering memory error. Use the `banana test` by turn on fetch MCP => ask local model to fetch and summarize the history of banana (banana has a very long history on wiki it turns out). It should run out of context memory sufficiently fast if `Context Shift` is not enabled.
- [x] [New] Ensure that user can change the Jinja chat template of individual model and it doesn't affect the template of other model
- [x] [New] Ensure that there is a recommended `llama.cpp` for each system and that it works out of the box for users. ✅

In Remote Model Providers:
- [x] Check that the following providers are presence:
	- [x] OpenAI ✅
	- [x] Anthropic ✅
	- [x] Cohere ✅
	- [x] OpenRouter ✅
	- [x] Mistral ✅
	- [x] Groq ✅
	- [x] Gemini ✅
	- [x] Hugging Face ✅
- [x] Models should appear as available on the selectable dropdown in chat input once some value is input in the API key field. (it could be the wrong API key)
- [x] Once a valid API key is used, user can select a model from that provider and chat without any error. 
- [x] Delete a model and ensure that it doesn't show up in the `Modesl` list view or in the selectable dropdown in chat input.
- [x] Ensure that a deleted model also not selectable or appear in old threads that used it.
- [x] Adding of new model manually works and user can chat with the newly added model without error (you can add back the model you just delete for testing)

In Custom Providers:
- [x] Ensure that user can create a new custom providers with the right baseURL and API key.
- [x] Click `Refresh` should retrieve a list of available models from the Custom Providers.
- [x] User can chat with the custom providers
- [x] Ensure that Custom Providers can be deleted and won't reappear in a new session

In general:
- [ ] Disabled Model Provider should not show up as selectable in chat input of new thread and old thread alike (old threads' chat input should show `Select Model` instead of disabled model)

#### In `Shortcuts`:

Make sure the following shortcut key combo is visible and works:
- [x] New chat ✅
- [x] Toggle Sidebar ✅
- [x] Zoom In ✅
- [x] Zoom Out ✅
- [x] Send Message ✅
- [x] New Line ✅
- [x] Navigation ✅

#### In `Hardware`:
Ensure that the following section information show up for hardware
- [x] Operating System ✅ 
- [x] CPU ✅
- [x] Memory ✅
- [x] GPU (If the machine has one) ✅
	- [x] Enabling and Disabling GPUs and ensure that model still run correctly in both mode
	- [x] Enabling or Disabling GPU should not affect the UI of the application

#### In `MCP Servers`:
- [x] Ensure that enabling the `Experimental Features` under `Advanced` in `General` will make the `MCP Servers` appear in the `Settings` list. ✅
- [x] Disable `Experimental Features` should also disable all the tools and not show up in chat input `Tools still show up in chat input`
- [x] Ensure that an user can create a MCP server successfully when enter in the correct information
- [x] Ensure that `Env` value is masked by `*` in the quick view.
- [x] If an `Env` value is missing, there should be a error pop up.
- [x] Ensure that deleted MCP server disappear from the `MCP Server` list without any error
- [x] Ensure that before a MCP is deleted, it will be disable itself first and won't appear on the tool list after deleted.
- [x] Ensure that when the content of a MCP server is edited, it will be updated and reflected accordingly in the UI and when running it.
- [x] Toggling enable and disabled of a MCP server work properly
- [x] A disabled MCP should not appear in the available tool list in chat input
- [x] An disabled MCP should not be callable even when forced prompt by the model (ensure there is no ghost MCP server)
- [x] Ensure that enabled MCP server start automatically upon starting of the application
- [x] An enabled MCP should show functions in the available tool list
- [x] User can use a model and call different tool from multiple enabled MCP servers in the same thread
- [x] If `Allow All MCP Tool Permissions` is disabled, in every new thread, before a tool is called, there should be a confirmation dialog pop up to confirm the action.
- [x] When the user click `Deny`, the tool call will not be executed and return a message indicate so in the tool call result.
- [x] When the user click `Allow Once` on the pop up, a confirmation dialog will appear again when the tool is called next time.
- [x] When the user click `Always Allow` on the pop up, the tool will retain permission and won't ask for confirmation again. (this applied at an individual tool level, not at the MCP server level)
- [x] If `Allow All MCP Tool Permissions` is enabled, in every new thread,  there should not be any confirmation dialog pop up when a tool is called.
- [x] [Windows OS] When a MCP tool is called, there is no terminal window pop-up or any flashing presence.
- [x] When the pop-up appear, make sure that the `Tool Parameters` is also shown with detail in the pop-up.

#### In `Local API Server`:
- [x] User can `Start Server` and chat with the default endpoint
	- [x] User should see the correct model name at `v1/models`
	- [x] User should be able to chat with it at `v1/chat/completions`
- [x] `Open Logs` show the correct query log send to the server and return from the server ✅
- [x] Make sure that changing all the parameter in `Server Configuration` is reflected when `Start Server`

#### In `HTTPS Proxy`:
- [ ] Model download request goes through proxy endpoint

## C. Hub
- [x] User can click `Download` to download a model ✅
- [x] User can cancel a model in the middle of downloading 🔥🔥🔥
- [x] User can add a Hugging Face model detail to the list by pasting a model name / model url into the search bar and press enter ✅
- [x] Clicking on a listing will open up the model card information within Jan and render the HTML properly
- [x] Clicking download work on the `Show variants` section ✅
- [x] Clicking download work inside the Model card HTML ✅

## D. Threads

#### In the left bar:
- [x] User can delete an old thread, and it won't reappear even when app restart
- [x] Change the title of the thread should update its last modification date and re-organise its position in the correct chronological order on the left bar.
- [x] The title of a new thread is the first message from the user.
- [x] Users can starred / un-starred threads accordingly
- [x] Starred threads should move to `Favourite` section and other threads should stay in `Recent`
- [x] Ensure that the search thread feature return accurate result based on thread titles and contents (including from both `Favourite` and `Recent`)
- [x] `Delete All` should delete only threads in the `Recents` section
- [x] `Unstar All` should un-star all of the `Favourites` threads and return them to `Recent`

#### In a thread:
- [x] When `New Chat` is clicked, the assistant is set as the last selected assistant, the model selected is set as the last used model, and the user can immediately chat with the model. 
- [x] User can conduct multi-turn conversation in a single thread without lost of data (given that `Context Shift` is not enabled)
- [x] User can change to a different model in the middle of a conversation in a thread and the model work.
- [x] User can click on `Regenerate` button on a returned message from the model to get a new response base on the previous context.
- [x] User can change `Assistant` in the middle of a conversation in a thread and the new assistant setting will be applied instead.
- [x] The chat windows can render and show all the content of a selected threads (including scroll up and down on long threads)
- [x] Old thread retained their setting as of the last update / usage
	- [x] Assistant option
	- [x] Model option (except if the model / model provider has been deleted or disabled)
- [x] User can send message with different type of text content (e.g text, emoji, ...)
- [x] When request model to generate a markdown table, the table is correctly formatted as returned from the model.
- [x] When model generate code, ensure that the code snippets is properly formatted according to the `Appearance -> Code Block` setting.
- [x] Users can edit their old message and and user can regenerate the answer based on the new message
- [x] User can click `Copy` to copy the model response
- [x] User can click `Delete` to delete either the user message or the model response.
- [x] The token speed appear when a response from model is being generated and the final value is show under the response. 
- [ ] [New] Make sure that user when using IME keyboard to type Chinese and Japanese character and they press `Enter`, the `Send` button doesn't trigger automatically after each words.

## E. Assistants
- [x] There is always at least one default Assistant which is Jan ✅
- [x] The default Jan assistant has `stream = True` by default 
- [x] User can create / edit a new assistant with different parameters and instructions choice. 🔥
- [x] When user delete the default Assistant, the next Assistant in line will be come the default Assistant and apply their setting to new chat accordingly.
- [x] User can create / edit assistant from within a Chat windows (on the top left)

## F. After checking everything else

In `Settings -> General`:
- [x] Change the location of the `App Data` to some other path that is not the default path
- [x] Click on `Reset` button in `Other` to factory reset the app:
	- [x] All threads deleted
	- [x] All Assistant deleted except for default Jan Assistant
	- [x] `App Data` location is reset back to default path
	- [x] Appearance reset
	- [x] Model Providers information all reset
		- [x] Llama.cpp setting reset
		- [x] API keys cleared
		- [x] All Custom Providers deleted
	- [x] Shortcuts reset
	- [x] MCP Servers reset
	- [x] Local API Server reset
	- [x] HTTPS Proxy reset
- [x] After closing the app, all models are unloaded properly
- [x] Locate to the data folder using the `App Data` path information => delete the folder => reopen the app to check that all the folder is re-created with all the necessary data.
- [x] Ensure that the uninstallation process removes the app successfully from the system.
## G. New App Installation
- [x] Clean up by deleting all the left over folder created by Jan
	- [ ] On MacOS
		- [ ] `~/Library/Application Support/Jan`
		- [ ] `~/Library/Caches/jan.ai.app`
	- [x] On Windows
		- [x] `C:\Users<Username>\AppData\Roaming\Jan\`
		- [x] `C:\Users<Username>\AppData\Local\jan.ai.app`
	- [ ] On Linux
		- [ ] `~/.cache/Jan`
		- [ ] `~/.cache/jan.ai.app`
		- [ ] `~/.local/share/Jan`
		- [ ] `~/.local/share/jan.ai.app`
- [x] Ensure that the fresh install of Jan launch
- [x] Do some basic check to see that all function still behaved as expected. To be extra careful, you can go through the whole list again. However, it is more advisable to just check to make sure that all the core functionality like `Thread` and `Model Providers` work as intended.

# II. After release
- [ ] Check that the App Updater works and user can update to the latest release without any problem
- [ ] App restarts after the user finished an update
- [ ] Repeat section `A. Initial update / migration Data check` above to verify that update is done correctly on live version
