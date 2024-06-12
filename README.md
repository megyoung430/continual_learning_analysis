# continual-learning

## Accessing the Database

### Setting up

In order to access the database, you need to create a '.dbconf' file in your home directory. To read from the database, you'll need the client section; to manage and update the settings for the animals, you'll need the manage section.

[client]
host=rodb.deneuro.org
user=mime
passwd=
port=3306

[manage]
user=derig
passwd=
host=db.deneuro.org

### Session and trial information in the database

The functions `getSessionParsedEvents`, `getSessionData`, and `getSessionSettings` will retrieve (and decode from JSON) different pieces of session information from the database.

What is the difference?
* **Parsed Events**: Parsed events is divided into **States** and **Events**. This keeps track of states entered and the events that occurred over the course of a trial. All the times are aligned to the start of the trial.
    - Both `parsed_events["States"]` and `parsed_events["Events"]` are dictionaries, whose keys are the name of the state (e.g., `'present_sound'`) and the name of the event (e.g., `'BotCIn'`), respectively.
    - The values for `parsed_events["States"]` is an (2,) array, representing the start and end times of the state.
    - The values for `parsed_events["Events"]` is an (N,) array, where n is the time that particular event occurred throughout the entire trial.
* **Data**: Data is whatever you save in `TrialPropertiestoSave` in your bpod code.
    - In `TrialPropertiestoSave`, the `parentlist` is `"n_done_trials"`, `"hit"`, `"viol"`, `"reward"`, and `"choice"`.
    - The continual learning protocol also stores:
        - `trial_info,` which logs relevant trial information and thus has the following properties:
            - `"trial_type"`: either 'train', 'test', or 'validation'.
            - `"sound"`: either 'task_1_sound_1', 'task_1_sound_2', 'task_2_sound_1', or 'task_2_sound_2'.
            - `"correct_port"`: either 'BotL' or 'BotR' for train or validation trials.
            - `"choice_port"`: either 'BotL' or 'BotR'. This will be '' if the animal doesn't make a choice and the trial times out.
            - `"reaction_time"`: the time from the presentation of the sound until the animal made the choice and poked into 'BotL' or 'BotR'. This will be [] if the animal doesn't make a choice and the trial times out.
            - `"guiding_light"`: whether or not the guiding light turned on for the train trial. This will be either 0 or 1 in train trials or NaN in test or validation trials.
            - `"time_until_light"`: time until the guiding light would turn on for the train tiral. This will be NaN for test or validation trials.
            - `"training_performance"`: current average performance on train trials.
            - `"validation_performance"`: current average performance on validation trials.
* **Settings**: Settings are the settings that are changed in that particular trial.
    - In a given training trial, the settings that might be changed are `target`, `correct_port`, `incorrect_port`, and `time_until_light`.
    - For example, the settings for a prey foraging trial could look like `target = 1`, `correct_port = 'BotL'`, `incorrect_port = 'BotR'`, `time_until_light = 2.38`.
