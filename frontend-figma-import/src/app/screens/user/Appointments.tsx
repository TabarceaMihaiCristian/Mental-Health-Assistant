import { Sidebar } from "../../components/layout/Sidebar";
import { Header } from "../../components/layout/Header";
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/Card";
import { Button } from "../../components/ui/Button";
import { Badge } from "../../components/ui/Badge";
import { Avatar } from "../../components/ui/Avatar";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "../../components/ui/Tabs";
import { EmptyState } from "../../components/ui/EmptyState";
import { Calendar, Clock, Video, MapPin, MoreVertical, X, RefreshCw } from "lucide-react";

export default function Appointments() {
  const upcomingAppointments = [
    {
      id: 1,
      specialist: "Dr. Michael Rodriguez",
      specialistAvatar: "",
      specialty: "Clinical Psychology",
      date: "May 13, 2026",
      time: "2:00 PM - 3:00 PM",
      mode: "video",
      status: "confirmed",
    },
    {
      id: 2,
      specialist: "Dr. Sarah Chen",
      specialistAvatar: "",
      specialty: "Cognitive Behavioral Therapy",
      date: "May 20, 2026",
      time: "10:00 AM - 11:00 AM",
      mode: "phone",
      status: "confirmed",
    },
  ];

  const pendingAppointments = [
    {
      id: 3,
      specialist: "Dr. James Wilson",
      specialistAvatar: "",
      specialty: "Trauma & PTSD",
      date: "May 15, 2026",
      time: "3:00 PM - 4:00 PM",
      mode: "in-person",
      location: "123 Main St, Los Angeles, CA",
      status: "requested",
    },
  ];

  const pastAppointments = [
    {
      id: 4,
      specialist: "Dr. Michael Rodriguez",
      specialistAvatar: "",
      specialty: "Clinical Psychology",
      date: "May 6, 2026",
      time: "2:00 PM - 3:00 PM",
      mode: "video",
      status: "completed",
    },
    {
      id: 5,
      specialist: "Dr. Sarah Chen",
      specialistAvatar: "",
      specialty: "Cognitive Behavioral Therapy",
      date: "Apr 29, 2026",
      time: "10:00 AM - 11:00 AM",
      mode: "phone",
      status: "completed",
    },
  ];

  const AppointmentCard = ({ appointment }: { appointment: any }) => (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-start gap-4">
            <Avatar
              fallback={appointment.specialist.split(" ").map((n: string) => n[0]).join("")}
              size="lg"
            />
            <div>
              <h3 className="font-[--font-weight-semibold] text-[--foreground]">
                {appointment.specialist}
              </h3>
              <p className="text-sm text-[--muted-foreground]">{appointment.specialty}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant={appointment.status as any}>{appointment.status}</Badge>
            <button className="p-2 rounded-[--radius-md] hover:bg-[--accent] transition-colors">
              <MoreVertical className="size-4 text-[--muted-foreground]" />
            </button>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="flex items-center gap-2 text-sm text-[--foreground]">
            <Calendar className="size-4 text-[--muted-foreground]" />
            <span>{appointment.date}</span>
          </div>
          <div className="flex items-center gap-2 text-sm text-[--foreground]">
            <Clock className="size-4 text-[--muted-foreground]" />
            <span>{appointment.time}</span>
          </div>
          {appointment.mode === "video" && (
            <div className="flex items-center gap-2 text-sm text-[--foreground]">
              <Video className="size-4 text-[--muted-foreground]" />
              <span>Video Call</span>
            </div>
          )}
          {appointment.mode === "in-person" && appointment.location && (
            <div className="flex items-center gap-2 text-sm text-[--foreground]">
              <MapPin className="size-4 text-[--muted-foreground]" />
              <span className="truncate">{appointment.location}</span>
            </div>
          )}
        </div>

        <div className="flex gap-2">
          {appointment.status === "confirmed" && (
            <>
              <Button variant="primary" size="sm" className="flex-1">
                {appointment.mode === "video" ? "Join Video" : "View Details"}
              </Button>
              <Button variant="ghost" size="sm">
                <RefreshCw className="size-4 mr-2" />
                Reschedule
              </Button>
              <Button variant="ghost" size="sm">
                <X className="size-4 mr-2" />
                Cancel
              </Button>
            </>
          )}
          {appointment.status === "requested" && (
            <Button variant="secondary" size="sm" className="flex-1">
              View Details
            </Button>
          )}
          {appointment.status === "completed" && (
            <Button variant="secondary" size="sm" className="flex-1">
              View Summary
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );

  return (
    <div className="flex min-h-screen bg-[--background]">
      <Sidebar role="user" />

      <div className="flex-1">
        <Header userName="Sarah Johnson" showSearch={false} />

        <main className="p-8">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-3xl font-[--font-weight-semibold] text-[--foreground] mb-2">
                My Appointments
              </h1>
              <p className="text-[--muted-foreground]">
                Manage your therapy sessions and appointments
              </p>
            </div>
            <Button variant="primary">
              <Calendar className="size-4 mr-2" />
              Book Appointment
            </Button>
          </div>

          <Tabs defaultValue="upcoming">
            <TabsList>
              <TabsTrigger value="upcoming">
                Upcoming ({upcomingAppointments.length})
              </TabsTrigger>
              <TabsTrigger value="pending">
                Pending ({pendingAppointments.length})
              </TabsTrigger>
              <TabsTrigger value="past">
                Past ({pastAppointments.length})
              </TabsTrigger>
            </TabsList>

            <TabsContent value="upcoming">
              <div className="space-y-4">
                {upcomingAppointments.map((appointment) => (
                  <AppointmentCard key={appointment.id} appointment={appointment} />
                ))}
                {upcomingAppointments.length === 0 && (
                  <Card>
                    <CardContent className="p-6">
                      <EmptyState
                        icon={<Calendar className="size-12" />}
                        title="No upcoming appointments"
                        description="You don't have any scheduled appointments"
                        action={<Button variant="primary">Book Appointment</Button>}
                      />
                    </CardContent>
                  </Card>
                )}
              </div>
            </TabsContent>

            <TabsContent value="pending">
              <div className="space-y-4">
                {pendingAppointments.map((appointment) => (
                  <AppointmentCard key={appointment.id} appointment={appointment} />
                ))}
                {pendingAppointments.length === 0 && (
                  <Card>
                    <CardContent className="p-6">
                      <EmptyState
                        icon={<Clock className="size-12" />}
                        title="No pending requests"
                        description="All your appointment requests have been processed"
                      />
                    </CardContent>
                  </Card>
                )}
              </div>
            </TabsContent>

            <TabsContent value="past">
              <div className="space-y-4">
                {pastAppointments.map((appointment) => (
                  <AppointmentCard key={appointment.id} appointment={appointment} />
                ))}
              </div>
            </TabsContent>
          </Tabs>
        </main>
      </div>
    </div>
  );
}
