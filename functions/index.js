const admin = require("firebase-admin");
admin.initializeApp();

// Import the function from setCustomClaims.js
const setCustomClaims = require("./setCustomClaims");

// Exports the function so it's deployable
exports.setCustomClaims = setCustomClaims;
