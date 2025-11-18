# IN PROGRESS

- return to main branch and revisit vbap render later
- make spatial instructions json
- dont deal with static objects for now

- update summary pipeline / analyze file - condense terminal output

# spatial instructions

\*\* create re packing system to take main audio file and object data json and produce a new json with info for spatialization in vbap render

- re label spatial instructions only with channels with audio
- split out all channels that contain audio as individual audio files (eveluate if necessary)
  - export each as object 1, 2, 3, etc
- package into "stagingForRender" folder

- explore : https://github.com/phenyque/pyvbap

# TO DO LATER

-make notebook

- start testing examples from https://zenodo.org/records/15268471
- width parameter

- bundle as one nice tool that can be accessed from command line

- build player in allolib that can cleanly handle these

- package the whole decoder into 1 alloapp - uses speaker layout json
