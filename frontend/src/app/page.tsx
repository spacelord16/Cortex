import { SystemStats } from "@/components/dashboard/SystemStats"
import { ChatInterface } from "@/components/chat/ChatInterface"
import { Separator } from "@/components/ui/separator"

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-8 bg-background text-foreground">
      <div className="z-10 w-full max-w-5xl items-center justify-between font-mono text-sm lg:flex">
        <p className="fixed left-0 top-0 flex w-full justify-center border-b bg-gradient-to-b from-zinc-200 pb-6 pt-8 backdrop-blur-2xl dark:border-neutral-800 dark:bg-zinc-800/30 dark:from-inherit lg:static lg:w-auto  lg:rounded-xl lg:border lg:bg-gray-200 lg:p-4 lg:dark:bg-zinc-800/30">
          Cortex OS v0.1.0
        </p>
        <div className="fixed bottom-0 left-0 flex h-48 w-full items-end justify-center bg-gradient-to-t from-white via-white dark:from-black dark:via-black lg:static lg:h-auto lg:w-auto lg:bg-none">
          <div className="pointer-events-none flex place-items-center gap-2 p-8 lg:pointer-events-auto lg:p-0">
             <span className="h-2 w-2 bg-green-500 rounded-full animate-pulse"></span>
             System Online
          </div>
        </div>
      </div>

      <div className="w-full max-w-5xl mt-8">
        <h2 className="text-2xl font-bold mb-4">System Status</h2>
        <SystemStats />
      </div>

      <Separator className="my-8 max-w-5xl" />

      <div className="w-full max-w-5xl flex-1">
        <h2 className="text-2xl font-bold mb-4">Agent Interface</h2>
        <ChatInterface />
      </div>
      
    </main>
  )
}
