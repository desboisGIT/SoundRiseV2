import { createTrack } from "../beats";

//###############################  UPLOAD BEAT SRIALIZER  ###############################

const MAX_TITLE_LENGTH = 80;

/**
 * validates the beat data
 * @param {Object} beatData
 * @returns {boolean} true if valid, otherwise false
 */
const validateBeatData = (beatData) => {
  console.log(beatData);
  if (!beatData.title || typeof beatData.title !== "string") {
    console.error("Title is required and must be a string.");
    return false;
  }
  if (beatData.title.trim().length > MAX_TITLE_LENGTH) {
    console.error(`Title must be at most ${MAX_TITLE_LENGTH} characters.`);
    return false;
  }
  if (!beatData.genre) {
    console.error("Genre is required.");
    return false;
  }

  /*if (Array.isArray(beatData.genre)) {
    if (!beatData.genre.every((g) => typeof g === "string")) {
      console.error("Each genre in the array must be a string.");
      return false;
    }
  } else if (typeof beatData.genre !== "string") {
    console.error("Genre must be a string or an array of strings.");
    return false;
  }*/

  if (!beatData.bpm || isNaN(parseInt(beatData.bpm, 10))) {
    console.error("BPM is required and must be a number.");
    return false;
  }

  if (!beatData.key || typeof beatData.key !== "string") {
    console.error("key is required and must be a string.");
    return false;
  }

  if (!beatData.cover_image) {
    console.error("cover image is required.");
    return false;
  }
  if (!beatData.licenses.length > 0) {
    console.error("license(s) is required.");
    return false;
  }
  console.log(listFileFromLicenses(beatData.licenses));
  return true;
};

const listFileFromLicenses = (licenseIDs) => {
  for (const licenseID of licenseIDs) {
  }
};

const validateFileFormat = () => {
  return null;
};

/**
 * Transforms a beat form data object into the format expected by the API.
 * @param {Object} beatData - The raw beat data from the form.
 * @returns {Object} The serialized beat data.
 */
export const serializeBeatData = (beatData) => {
  if (!validateBeatData(beatData)) {
    return "error";
  }
  var serialized = {
    title: beatData.title.trim(),
    genre: beatData.genre.toLowerCase(),
    bpm: parseInt(beatData.bpm, 10),
    key: beatData.key,
    is_public: beatData.is_public ? true : false,
    // For files, you might attach them to a FormData later
    // or perform any special formatting.
    // Also, if you have arrays or nested objects, transform them accordingly.
    co_artists: beatData.co_artists,
    licenses: beatData.licenses,
  };

  // Include any additional transformation logic here

  return serialized;
};

//#######################################################################################
