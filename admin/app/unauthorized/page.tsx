import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { AlertTriangle } from "lucide-react"
import Link from "next/link"

export default function UnauthorizedPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4 py-12 sm:px-6 lg:px-8">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1">
          <div className="flex justify-center mb-4">
            <div className="rounded-full bg-red-100 p-3">
              <AlertTriangle className="h-6 w-6 text-red-600" />
            </div>
          </div>
          <CardTitle className="text-2xl font-bold text-center">Access Denied</CardTitle>
          <CardDescription className="text-center">You do not have permission to access this page.</CardDescription>
        </CardHeader>
        <CardContent className="text-center">
          <p className="mb-4">Please contact your administrator if you believe this is an error.</p>
        </CardContent>
        <CardFooter>
          <Button asChild className="w-full">
            <Link href="/">Return to Dashboard</Link>
          </Button>
        </CardFooter>
      </Card>
    </div>
  )
}
