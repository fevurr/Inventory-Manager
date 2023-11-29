const functions = require("firebase-functions");
const admin = require("firebase-admin");

admin.initializeApp();

exports.setCustomClaims = functions.auth.user().onCreate((user) => {
  if (user.email?.endsWith("@cliftauto.com")) {
    return admin.auth().setCustomUserClaims(user.uid, {
      isCliftAutoUser: true,
    });
  }

  return null;
});
