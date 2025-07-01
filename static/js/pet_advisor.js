const pets = [
  {
    name: "Wolf",
    role: "Main",
    description: "DPS + Kontrolle",
    skills: ["Phantom Klinge", "Flammenling", "Geist Flamme", "Zorn Ling", "Riss Leere"],
    optional: ["Blitzsiegel"],
    tags: ["DPS", "Silence", "Anti-Passiv"]
  },
  {
    name: "Misha",
    role: "Tank",
    description: "Überleben + Sustain",
    skills: ["Wut Leitfaden", "Aufräumen Feder", "Phantom Schild", "Äther. Verteid.", "Wächtergeist"],
    optional: ["Geistwind"],
    tags: ["DEF", "Heilung", "Zorn"]
  },
  {
    name: "Rottweiler",
    role: "Support",
    description: "Kontrolle + Verstärkung",
    skills: ["Blitzsiegel", "Riss Leere", "Zorn Ling", "Wächtergeist", "Geist Flamme"],
    optional: ["Flammenling"],
    tags: ["Anti-Zorn", "Silence", "Buff"]
  }
];

function PetAdvisorDashboard() {
  const [selectedRole, setSelectedRole] = React.useState("All");
  const filteredPets =
    selectedRole === "All"
      ? pets
      : pets.filter((p) => p.role.toLowerCase() === selectedRole.toLowerCase());

  return (
    <div className="p-4 space-y-4">
      <h1 className="text-2xl font-bold">🐾 Pet Advisor Dashboard</h1>
      <div className="flex gap-2">
        {['All', 'Main', 'Tank', 'Support'].map((r) => (
          <button
            key={r}
            onClick={() => setSelectedRole(r)}
            className={
              'px-2 py-1 rounded ' +
              (selectedRole === r ? 'bg-orange-500 text-white' : 'bg-gray-700')
            }
          >
            {r}
          </button>
        ))}
      </div>
      <div className="grid md:grid-cols-3 gap-4">
        {filteredPets.map((pet) => (
          <div key={pet.name} className="rounded-2xl shadow p-4 space-y-2 bg-gray-800">
            <div className="text-xl font-semibold">{pet.name}</div>
            <div className="text-sm opacity-80">{pet.description}</div>
            <div className="space-y-1">
              <div className="font-medium">Empfohlene Skills:</div>
              <ul className="list-disc list-inside text-sm">
                {pet.skills.map((skill) => (
                  <li key={skill}>{skill}</li>
                ))}
              </ul>
              <div className="text-xs italic">Optional: {pet.optional.join(', ')}</div>
            </div>
            <div className="flex flex-wrap gap-1 pt-2">
              {pet.tags.map((tag) => (
                <span
                  key={tag}
                  className="bg-gray-600 rounded px-2 py-0.5 text-xs"
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

document.addEventListener('DOMContentLoaded', () => {
  const rootEl = document.getElementById('pet-advisor-root');
  if (!rootEl) return;
  const root = ReactDOM.createRoot(rootEl);
  root.render(<PetAdvisorDashboard />);
});
