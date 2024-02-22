# battlecabbage-media

This respository is host to a larger data creation and management tools for a faux media company. This project makes use of many different services

- Azure Open AI
    - GPT4 Models including GPT-4 Turbo for Vision capabalities
    - Dalle3 

## Media Generation

![Media Generation Flow](assets/images/media_generation_flow.jpeg)

### Step-By-Step:
1) [Media Generator](library-management/generators/media_generator.py) heavily utilitizes the [prompts.json](library-management/templates/prompts.json) containing handwritten prompts for various Azure OpenAI model endpoints and their uses. The prompts are written to be dynamic and are filled in at random from the category json files (e.g. [genres.json](library-management/templates/genres.json)). Its like a movie maker madlib!
2) The stitched together prompt is sent to a generative Text model to build a new movie including info like its title, tagline and description (and much more) as a new movie completion.
3) Using the 'movie' completion, we send various details again to a generative text model to ask it to create a prompt that would be used in a generative image model (Dalle in our case).
4) The image prompt is sent to a generative image model to create a poster to be used for the movie, we also give it a list of fonts and say pick one you think is best.
5) The generated image is sent to the GPT Vision model to suggest what location on the poster text should go and what color the font should be.
6) The title is placed on the image in the color suggested by the Vision model, saved as a jpeg and the details of the movie are saved as a JSON file.

**Voila!** We just used Azure OpenAI generative models to make a movie from a general description of what the movie should entail and it spit out a full film right down to the poster to go with it.  Check out the [example poster](assets/examples/images/generated_poster_1.jpg) and [example movie](assets/examples/json/generated_movie_1.json) to see some example results.