# A technique to resize images with bounding boxes

## Part 1: the challenge
I'm currently doing a project with the Egyptologie department of the Sorbonne. The purpose is to determine which scribe has written a papyrus based on the calligraphy of the scribe.

Their first idea was to take the caracteres that were the most written in the papyrus because their idea was that is the letter that you write the most that define your personnal calligraphy, bacause it's very likely that these letters are written faster that unusual letters.

Thus, we needed to make a double classification with first, the caracteres, and then after with the scribes. After, we planned on making a clustering algorithm for the scribes that were not in our database.




Dwnside with working with polars: No integration with Cv2 and with Tf