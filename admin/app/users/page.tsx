import { redirect } from "next/navigation"
import { getServerSession } from "next-auth/next"
import { authOptions } from "@/lib/auth"
import UserManagement from "@/components/user-management"

export default async function UsersPage() {
  const session = await getServerSession(authOptions)

  if (!session) {
    redirect("/login")
  }

  // Only admins can access this page
  if (session.user.role !== "admin") {
    redirect("/unauthorized")
  }

  return (
    <div className="container mx-auto py-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold">User Management</h1>
          <p className="text-muted-foreground">Manage system users and their permissions</p>
        </div>
      </div>

      <UserManagement />
    </div>
  )
}
