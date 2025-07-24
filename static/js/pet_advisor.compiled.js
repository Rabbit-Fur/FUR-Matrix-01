"use strict";

var _slicedToArray = (function () { function sliceIterator(arr, i) { var _arr = []; var _n = true; var _d = false; var _e = undefined; try { for (var _i = arr[Symbol.iterator](), _s; !(_n = (_s = _i.next()).done); _n = true) { _arr.push(_s.value); if (i && _arr.length === i) break; } } catch (err) { _d = true; _e = err; } finally { try { if (!_n && _i["return"]) _i["return"](); } finally { if (_d) throw _e; } } return _arr; } return function (arr, i) { if (Array.isArray(arr)) { return arr; } else if (Symbol.iterator in Object(arr)) { return sliceIterator(arr, i); } else { throw new TypeError("Invalid attempt to destructure non-iterable instance"); } }; })();

var pets = [{
  name: "Wolf",
  role: "Main",
  description: "DPS + Kontrolle",
  skills: ["Phantom Klinge", "Flammenling", "Geist Flamme", "Zorn Ling", "Riss Leere"],
  optional: ["Blitzsiegel"],
  tags: ["DPS", "Silence", "Anti-Passiv"]
}, {
  name: "Misha",
  role: "Tank",
  description: "Überleben + Sustain",
  skills: ["Wut Leitfaden", "Aufräumen Feder", "Phantom Schild", "Äther. Verteid.", "Wächtergeist"],
  optional: ["Geistwind"],
  tags: ["DEF", "Heilung", "Zorn"]
}, {
  name: "Rottweiler",
  role: "Support",
  description: "Kontrolle + Verstärkung",
  skills: ["Blitzsiegel", "Riss Leere", "Zorn Ling", "Wächtergeist", "Geist Flamme"],
  optional: ["Flammenling"],
  tags: ["Anti-Zorn", "Silence", "Buff"]
}];

function PetAdvisorDashboard() {
  var _React$useState = React.useState("All");

  var _React$useState2 = _slicedToArray(_React$useState, 2);

  var selectedRole = _React$useState2[0];
  var setSelectedRole = _React$useState2[1];

  var filteredPets = selectedRole === "All" ? pets : pets.filter(function (p) {
    return p.role.toLowerCase() === selectedRole.toLowerCase();
  });

  return React.createElement(
    "div",
    { className: "p-4 space-y-4" },
    React.createElement(
      "h1",
      { className: "text-2xl font-bold" },
      "🐾 Pet Advisor Dashboard"
    ),
    React.createElement(
      "div",
      { className: "flex gap-2" },
      ['All', 'Main', 'Tank', 'Support'].map(function (r) {
        return React.createElement(
          "button",
          {
            key: r,
            onClick: function () {
              return setSelectedRole(r);
            },
            className: 'px-2 py-1 rounded ' + (selectedRole === r ? 'bg-orange-500 text-white' : 'bg-gray-700')
          },
          r
        );
      })
    ),
    React.createElement(
      "div",
      { className: "grid md:grid-cols-3 gap-4" },
      filteredPets.map(function (pet) {
        return React.createElement(
          "div",
          { key: pet.name, className: "rounded-2xl shadow p-4 space-y-2 bg-gray-800" },
          React.createElement(
            "div",
            { className: "text-xl font-semibold" },
            pet.name
          ),
          React.createElement(
            "div",
            { className: "text-sm opacity-80" },
            pet.description
          ),
          React.createElement(
            "div",
            { className: "space-y-1" },
            React.createElement(
              "div",
              { className: "font-medium" },
              "Empfohlene Skills:"
            ),
            React.createElement(
              "ul",
              { className: "list-disc list-inside text-sm" },
              pet.skills.map(function (skill) {
                return React.createElement(
                  "li",
                  { key: skill },
                  skill
                );
              })
            ),
            React.createElement(
              "div",
              { className: "text-xs italic" },
              "Optional: ",
              pet.optional.join(', ')
            )
          ),
          React.createElement(
            "div",
            { className: "flex flex-wrap gap-1 pt-2" },
            pet.tags.map(function (tag) {
              return React.createElement(
                "span",
                {
                  key: tag,
                  className: "bg-gray-600 rounded px-2 py-0.5 text-xs"
                },
                tag
              );
            })
          )
        );
      })
    )
  );
}

document.addEventListener('DOMContentLoaded', function () {
  var rootEl = document.getElementById('pet-advisor-root');
  if (!rootEl) return;
  var root = ReactDOM.createRoot(rootEl);
  root.render(React.createElement(PetAdvisorDashboard, null));
});
