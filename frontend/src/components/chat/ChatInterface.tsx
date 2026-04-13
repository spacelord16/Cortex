"use client"

import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Send, Bot, User } from "lucide-react"

interface Message {
  role: "user" | "assistant"
  content: string
  sender?: string
}

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: "smooth" })
    }
  }, [messages])

  const sendMessage = async () => {
    if (!input.trim()) return

    const userMsg: Message = { role: "user", content: input }
    setMessages((prev) => [...prev, userMsg])
    setInput("")
    setLoading(true)

    try {
      const response = await fetch(`http://localhost:8000/chat?message=${encodeURIComponent(userMsg.content)}`, {
        method: "POST",
      })

      if (!response.ok) throw new Error("Network error")
      if (!response.body) throw new Error("No response body")

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      
      setMessages((prev) => [...prev, { role: "assistant", content: "", sender: "Cortex" }])

      let buffer = ""

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        
        buffer += decoder.decode(value, { stream: true })
        // Split by newlines to get individual JSON NDJSON lines
        const lines = buffer.split("\n")
        
        // The last element might be incomplete, so keep it in the buffer
        buffer = lines.pop() || ""

        for (const line of lines) {
           if (!line.trim()) continue
           
           try {
             const json = JSON.parse(line)
             setMessages((prev) => {
                const newMsgs = [...prev]
                const last = newMsgs[newMsgs.length - 1]
                
                // If the last message is an empty assistant placeholder, update it.
                // Otherwise, if it's a completely new node update, append a new message bubble.
                if (last.role === "assistant" && last.content === "") {
                  return [...newMsgs.slice(0, -1), { role: "assistant", content: json.content, sender: json.sender }]
                } else if (last.role === "assistant" && json.content.trim() !== "") {
                  // Only append if it's not a weird empty string overwrite from the LLM
                  return [...newMsgs, { role: "assistant", content: json.content, sender: json.sender }]
                }
                
                return newMsgs
             })
           } catch (e) {
             console.error("Error parsing chunk", e, "Line:", line)
           }
        }
      }

    } catch (error) {
      console.error("Chat error", error)
      setMessages((prev) => [...prev, { role: "assistant", content: "Error connecting to Cortex." }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card className="h-[600px] flex flex-col">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Bot className="w-5 h-5" />
          Cortex Chat
        </CardTitle>
      </CardHeader>
      <CardContent className="flex-1 p-0 overflow-hidden">
        <ScrollArea className="h-full p-4">
          <div className="flex flex-col gap-4">
            {messages.map((msg, i) => (
              <div key={i} className={`flex gap-3 ${msg.role === "user" ? "flex-row-reverse" : ""}`}>
                <Avatar className="w-8 h-8">
                  <AvatarFallback>{msg.role === "user" ? "ME" : "AI"}</AvatarFallback>
                  <AvatarImage src={msg.role === "user" ? "/user.png" : "/bot.png"} />
                </Avatar>
                <div className={`p-3 rounded-lg max-w-[80%] ${msg.role === "user" ? "bg-primary text-primary-foreground" : "bg-muted"}`}>
                  {msg.sender && <div className="text-xs font-bold mb-1 opacity-70">{msg.sender}</div>}
                  <div className="whitespace-pre-wrap">{msg.content}</div>
                </div>
              </div>
            ))}
            {/* Typing indicator — shown while the backend is thinking */}
            {loading && (
              <div className="flex gap-3">
                <Avatar className="w-8 h-8">
                  <AvatarFallback>AI</AvatarFallback>
                </Avatar>
                <div className="bg-muted p-3 rounded-lg flex items-center gap-1">
                  <span className="text-xs text-muted-foreground mr-1">Cortex is thinking</span>
                  <span className="w-1.5 h-1.5 bg-current rounded-full animate-bounce [animation-delay:-0.3s]"/>
                  <span className="w-1.5 h-1.5 bg-current rounded-full animate-bounce [animation-delay:-0.15s]"/>
                  <span className="w-1.5 h-1.5 bg-current rounded-full animate-bounce"/>
                </div>
              </div>
            )}
            <div ref={scrollRef} />
          </div>
        </ScrollArea>
      </CardContent>
      <CardFooter className="p-4 pt-0">
        <form
          className="flex w-full gap-2"
          onSubmit={(e) => {
            e.preventDefault()
            sendMessage()
          }}
        >
          <Input 
            value={input} 
            onChange={(e) => setInput(e.target.value)} 
            placeholder="Type a message..." 
            disabled={loading}
          />
          <Button type="submit" disabled={loading}>
            <Send className="w-4 h-4" />
          </Button>
        </form>
      </CardFooter>
    </Card>
  )
}
