import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import { Badge } from "@/components/ui/badge";

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

export default function PetAdvisorDashboard() {
  const [selectedRole, setSelectedRole] = useState("All");

  const filteredPets =
    selectedRole === "All"
      ? pets
      : pets.filter((p) => p.role.toLowerCase() === selectedRole.toLowerCase());

  return (
    <div className="p-4 space-y-4">
      <h1 className="text-2xl font-bold">🐾 Pet Advisor Dashboard</h1>
      <ToggleGroup
        type="single"
        className="flex gap-2"
        value={selectedRole}
        onValueChange={(v) => setSelectedRole(v || "All")}
      >
        <ToggleGroupItem value="All">Alle</ToggleGroupItem>
        <ToggleGroupItem value="Main">Main</ToggleGroupItem>
        <ToggleGroupItem value="Tank">Tank</ToggleGroupItem>
        <ToggleGroupItem value="Support">Support</ToggleGroupItem>
      </ToggleGroup>

      <div className="grid md:grid-cols-3 gap-4">
        {filteredPets.map((pet) => (
          <Card key={pet.name} className="rounded-2xl shadow">
            <CardContent className="p-4 space-y-2">
              <div className="text-xl font-semibold">{pet.name}</div>
              <div className="text-sm text-muted-foreground">{pet.description}</div>
              <div className="space-y-1">
                <div className="font-medium">Empfohlene Skills:</div>
                <ul className="list-disc list-inside text-sm">
                  {pet.skills.map((skill) => (
                    <li key={skill}>{skill}</li>
                  ))}
                </ul>
                <div className="text-xs italic">
                  Optional: {pet.optional.join(", ")}
                </div>
              </div>
              <div className="flex flex-wrap gap-1 pt-2">
                {pet.tags.map((tag) => (
                  <Badge key={tag} variant="secondary">
                    {tag}
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
