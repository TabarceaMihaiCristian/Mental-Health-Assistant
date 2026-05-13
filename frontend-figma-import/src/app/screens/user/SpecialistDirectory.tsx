import { useState } from "react";
import { Sidebar } from "../../components/layout/Sidebar";
import { Header } from "../../components/layout/Header";
import { Card, CardContent } from "../../components/ui/Card";
import { Button } from "../../components/ui/Button";
import { Input } from "../../components/ui/Input";
import { Select } from "../../components/ui/Select";
import { Avatar } from "../../components/ui/Avatar";
import { EmptyState } from "../../components/ui/EmptyState";
import { LoadingSpinner } from "../../components/ui/LoadingSpinner";
import { Star, MapPin, Video, Phone, Users, Filter } from "lucide-react";

export default function SpecialistDirectory() {
  const [loading] = useState(false);
  const [showFilters, setShowFilters] = useState(true);

  const specialists = [
    {
      id: 1,
      name: "Dr. Michael Rodriguez",
      specialty: "Clinical Psychology",
      city: "San Francisco, CA",
      rating: 4.9,
      reviews: 127,
      modes: ["video", "phone", "in-person"],
      avatar: "",
    },
    {
      id: 2,
      name: "Dr. Sarah Chen",
      specialty: "Cognitive Behavioral Therapy",
      city: "New York, NY",
      rating: 4.8,
      reviews: 98,
      modes: ["video", "phone"],
      avatar: "",
    },
    {
      id: 3,
      name: "Dr. James Wilson",
      specialty: "Trauma & PTSD",
      city: "Los Angeles, CA",
      rating: 4.9,
      reviews: 143,
      modes: ["video", "in-person"],
      avatar: "",
    },
    {
      id: 4,
      name: "Dr. Emily Martinez",
      specialty: "Anxiety & Depression",
      city: "Chicago, IL",
      rating: 4.7,
      reviews: 89,
      modes: ["video", "phone"],
      avatar: "",
    },
  ];

  if (loading) {
    return (
      <div className="flex min-h-screen bg-[--background]">
        <Sidebar role="user" />
        <div className="flex-1">
          <Header userName="Sarah Johnson" showSearch />
          <main className="p-8">
            <LoadingSpinner size="lg" className="py-20" />
          </main>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-[--background]">
      <Sidebar role="user" />

      <div className="flex-1">
        <Header userName="Sarah Johnson" showSearch />

        <main className="p-8">
          <div className="mb-8">
            <h1 className="text-3xl font-[--font-weight-semibold] text-[--foreground] mb-2">
              Find a Specialist
            </h1>
            <p className="text-[--muted-foreground]">
              Browse our network of licensed mental health professionals
            </p>
          </div>

          <div className="flex gap-6">
            {/* Filters Sidebar */}
            {showFilters && (
              <div className="w-72 flex-shrink-0">
                <Card>
                  <CardContent className="p-6 space-y-5">
                    <div className="flex items-center justify-between">
                      <h3 className="font-[--font-weight-semibold] text-[--foreground]">Filters</h3>
                      <Button variant="ghost" size="sm" onClick={() => setShowFilters(false)}>
                        Hide
                      </Button>
                    </div>

                    <Select
                      label="Specialty"
                      options={[
                        { value: "", label: "All Specialties" },
                        { value: "anxiety", label: "Anxiety & Depression" },
                        { value: "cbt", label: "Cognitive Behavioral Therapy" },
                        { value: "trauma", label: "Trauma & PTSD" },
                        { value: "relationships", label: "Relationships" },
                      ]}
                    />

                    <Input
                      type="text"
                      label="City or Zip Code"
                      placeholder="e.g., San Francisco"
                    />

                    <div>
                      <label className="block mb-2 text-[--foreground]">Consultation Mode</label>
                      <div className="space-y-2">
                        <label className="flex items-center gap-2 cursor-pointer">
                          <input type="checkbox" className="size-4 rounded accent-[--primary]" defaultChecked />
                          <span className="text-sm">Video</span>
                        </label>
                        <label className="flex items-center gap-2 cursor-pointer">
                          <input type="checkbox" className="size-4 rounded accent-[--primary]" />
                          <span className="text-sm">Phone</span>
                        </label>
                        <label className="flex items-center gap-2 cursor-pointer">
                          <input type="checkbox" className="size-4 rounded accent-[--primary]" />
                          <span className="text-sm">In-Person</span>
                        </label>
                      </div>
                    </div>

                    <div>
                      <label className="block mb-2 text-[--foreground]">Minimum Rating</label>
                      <div className="flex items-center gap-2">
                        <Star className="size-5 text-[--amber-500]" fill="var(--amber-500)" />
                        <input
                          type="range"
                          min="0"
                          max="5"
                          step="0.5"
                          defaultValue="4"
                          className="flex-1"
                        />
                        <span className="text-sm text-[--foreground] w-8">4.0+</span>
                      </div>
                    </div>

                    <Button variant="secondary" className="w-full">
                      Apply Filters
                    </Button>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* Results */}
            <div className="flex-1">
              <div className="flex items-center justify-between mb-6">
                <p className="text-[--muted-foreground]">
                  Showing <span className="font-[--font-weight-medium] text-[--foreground]">4</span> specialists
                </p>
                <div className="flex items-center gap-3">
                  {!showFilters && (
                    <Button variant="ghost" size="sm" onClick={() => setShowFilters(true)}>
                      <Filter className="size-4 mr-2" />
                      Show Filters
                    </Button>
                  )}
                  <Select
                    options={[
                      { value: "rating", label: "Highest Rated" },
                      { value: "reviews", label: "Most Reviews" },
                      { value: "name", label: "Name A-Z" },
                    ]}
                  />
                </div>
              </div>

              <div className="space-y-4">
                {specialists.map((specialist) => (
                  <Card key={specialist.id} className="hover:shadow-[--shadow-md] transition-shadow">
                    <CardContent className="p-6">
                      <div className="flex items-start gap-6">
                        <Avatar
                          fallback={specialist.name.split(" ").map(n => n[0]).join("")}
                          size="xl"
                        />

                        <div className="flex-1">
                          <div className="flex items-start justify-between mb-2">
                            <div>
                              <h3 className="text-xl font-[--font-weight-semibold] text-[--foreground]">
                                {specialist.name}
                              </h3>
                              <p className="text-[--muted-foreground]">{specialist.specialty}</p>
                            </div>
                            <Button variant="primary">View Profile</Button>
                          </div>

                          <div className="flex items-center gap-4 text-sm text-[--foreground] mb-3">
                            <div className="flex items-center gap-1">
                              <Star className="size-4 text-[--amber-500]" fill="var(--amber-500)" />
                              <span className="font-[--font-weight-medium]">{specialist.rating}</span>
                              <span className="text-[--muted-foreground]">({specialist.reviews} reviews)</span>
                            </div>
                            <div className="flex items-center gap-2">
                              <MapPin className="size-4 text-[--muted-foreground]" />
                              <span>{specialist.city}</span>
                            </div>
                          </div>

                          <div className="flex items-center gap-2">
                            <span className="text-sm text-[--muted-foreground]">Consultation modes:</span>
                            {specialist.modes.includes("video") && (
                              <div className="flex items-center gap-1 px-2 py-1 rounded-full bg-[--teal-100] text-[--teal-700] text-xs">
                                <Video className="size-3" />
                                <span>Video</span>
                              </div>
                            )}
                            {specialist.modes.includes("phone") && (
                              <div className="flex items-center gap-1 px-2 py-1 rounded-full bg-[--sage-100] text-[--sage-700] text-xs">
                                <Phone className="size-3" />
                                <span>Phone</span>
                              </div>
                            )}
                            {specialist.modes.includes("in-person") && (
                              <div className="flex items-center gap-1 px-2 py-1 rounded-full bg-[--sand-200] text-[--sand-800] text-xs">
                                <Users className="size-3" />
                                <span>In-Person</span>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>

              {specialists.length === 0 && (
                <Card>
                  <CardContent className="p-6">
                    <EmptyState
                      icon={<Users className="size-12" />}
                      title="No specialists found"
                      description="Try adjusting your filters to see more results"
                      action={<Button variant="secondary">Clear Filters</Button>}
                    />
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
