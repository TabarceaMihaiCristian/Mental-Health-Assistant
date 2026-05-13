import { Sidebar } from "../../components/layout/Sidebar";
import { Header } from "../../components/layout/Header";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../../components/ui/Card";
import { Button } from "../../components/ui/Button";
import { Badge } from "../../components/ui/Badge";
import { Avatar } from "../../components/ui/Avatar";
import { Calendar, Clock, CheckCircle, XCircle, Users, TrendingUp } from "lucide-react";

export default function SpecialistDashboard() {
  const todayAppointments = [
    {
      id: 1,
      patient: "Sarah Johnson",
      time: "10:00 AM",
      duration: "60 min",
      status: "confirmed",
      mode: "video",
    },
    {
      id: 2,
      patient: "Michael Brown",
      time: "2:00 PM",
      duration: "60 min",
      status: "confirmed",
      mode: "phone",
    },
    {
      id: 3,
      patient: "Emily Davis",
      time: "4:00 PM",
      duration: "45 min",
      status: "confirmed",
      mode: "in-person",
    },
  ];

  const pendingRequests = [
    {
      id: 4,
      patient: "John Smith",
      requestedDate: "May 15, 2026",
      requestedTime: "3:00 PM",
      duration: "60 min",
    },
    {
      id: 5,
      patient: "Lisa Martinez",
      requestedDate: "May 18, 2026",
      requestedTime: "11:00 AM",
      duration: "60 min",
    },
  ];

  return (
    <div className="flex min-h-screen bg-[--background]">
      <Sidebar role="specialist" />

      <div className="flex-1">
        <Header userName="Dr. Michael Rodriguez" showSearch={false} />

        <main className="p-8">
          <div className="mb-8">
            <h1 className="text-3xl font-[--font-weight-semibold] text-[--foreground] mb-2">
              Good morning, Dr. Rodriguez
            </h1>
            <p className="text-[--muted-foreground]">
              Tuesday, May 12, 2026
            </p>
          </div>

          {/* Stats Overview */}
          <div className="grid md:grid-cols-4 gap-6 mb-8">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-[--muted-foreground] mb-1">Today's Appointments</p>
                    <p className="text-3xl font-[--font-weight-semibold] text-[--foreground]">
                      {todayAppointments.length}
                    </p>
                  </div>
                  <div className="size-12 rounded-[--radius-lg] bg-[--teal-100] flex items-center justify-center">
                    <Calendar className="size-6 text-[--teal-700]" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-[--muted-foreground] mb-1">Pending Requests</p>
                    <p className="text-3xl font-[--font-weight-semibold] text-[--foreground]">
                      {pendingRequests.length}
                    </p>
                  </div>
                  <div className="size-12 rounded-[--radius-lg] bg-[--amber-100] flex items-center justify-center">
                    <Clock className="size-6 text-[--amber-700]" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-[--muted-foreground] mb-1">Active Clients</p>
                    <p className="text-3xl font-[--font-weight-semibold] text-[--foreground]">24</p>
                  </div>
                  <div className="size-12 rounded-[--radius-lg] bg-[--sage-100] flex items-center justify-center">
                    <Users className="size-6 text-[--sage-700]" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-[--muted-foreground] mb-1">This Week</p>
                    <p className="text-3xl font-[--font-weight-semibold] text-[--foreground]">18</p>
                    <p className="text-xs text-[--success] flex items-center gap-1 mt-1">
                      <TrendingUp className="size-3" />
                      <span>+12% from last week</span>
                    </p>
                  </div>
                  <div className="size-12 rounded-[--radius-lg] bg-[--sand-200] flex items-center justify-center">
                    <Calendar className="size-6 text-[--sand-800]" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            {/* Left Column - Today's Schedule */}
            <div className="md:col-span-2 space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Today's Schedule</CardTitle>
                  <CardDescription>Your appointments for Tuesday, May 12</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {todayAppointments.map((appointment, index) => (
                      <div key={appointment.id}>
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-4">
                            <div className="text-center">
                              <p className="text-sm font-[--font-weight-semibold] text-[--foreground]">
                                {appointment.time}
                              </p>
                              <p className="text-xs text-[--muted-foreground]">
                                {appointment.duration}
                              </p>
                            </div>
                            <div className="w-px h-12 bg-[--border]" />
                            <Avatar fallback={appointment.patient.split(" ").map(n => n[0]).join("")} />
                            <div>
                              <p className="font-[--font-weight-semibold] text-[--foreground]">
                                {appointment.patient}
                              </p>
                              <p className="text-sm text-[--muted-foreground] capitalize">
                                {appointment.mode} session
                              </p>
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            <Badge variant="confirmed">{appointment.status}</Badge>
                            <Button variant="secondary" size="sm">View</Button>
                          </div>
                        </div>
                        {index < todayAppointments.length - 1 && (
                          <div className="my-4 border-t border-[--border]" />
                        )}
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Quick Actions</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-4">
                    <Button variant="secondary" className="h-auto py-4 flex-col gap-2">
                      <Calendar className="size-6" />
                      <span>Manage Schedule</span>
                    </Button>
                    <Button variant="secondary" className="h-auto py-4 flex-col gap-2">
                      <Users className="size-6" />
                      <span>View Clients</span>
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Right Column - Pending Requests */}
            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle>Pending Requests</CardTitle>
                    <Badge variant="default">{pendingRequests.length}</Badge>
                  </div>
                  <CardDescription>New appointment requests</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {pendingRequests.map((request) => (
                      <div key={request.id} className="p-4 rounded-[--radius-lg] border border-[--border]">
                        <div className="flex items-start gap-3 mb-3">
                          <Avatar fallback={request.patient.split(" ").map(n => n[0]).join("")} size="sm" />
                          <div className="flex-1">
                            <p className="font-[--font-weight-semibold] text-[--foreground] text-sm">
                              {request.patient}
                            </p>
                            <p className="text-xs text-[--muted-foreground]">
                              {request.requestedDate} at {request.requestedTime}
                            </p>
                          </div>
                        </div>
                        <div className="flex gap-2">
                          <Button variant="success" size="sm" className="flex-1">
                            <CheckCircle className="size-3 mr-1" />
                            Accept
                          </Button>
                          <Button variant="ghost" size="sm">
                            <XCircle className="size-3 mr-1" />
                            Decline
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
