import { format } from "date-fns";
import { Calendar as CalendarIcon } from "lucide-react";

import { cn } from "@/lib/utils";
import { Button } from "@/components/_ui/button";
import { Calendar } from "@/components/_ui/calendar";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/_ui/popover";

interface Props {
  date: Date | undefined;
  setDate: (date: Date | undefined) => void;
  className?: string;
}

export function DatePicker({ date, setDate, className }: Props) {
  const handleSelect = (selectedDate: Date | undefined) => {
    console.log("selectedDate in DatePicker", selectedDate); // Log for debugging
    setDate(selectedDate);
  };

  return (
    <div className={cn("grid gap-2", className)}>
      <Popover>
        <PopoverTrigger asChild>
          <Button
            id="date"
            variant={"outline"}
            className={cn(
              "w-[300px] justify-start text-left font-normal",
              !date && "text-muted-foreground"
            )}
          >
            <CalendarIcon className="mr-2 h-4 w-4" />
            {date ? format(date, "LLL dd, y") : <span>Pick a date</span>}
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-auto p-0" align="start">
          <Calendar
            initialFocus
            mode="single"
            selected={date}
            onSelect={handleSelect}
          />
        </PopoverContent>
      </Popover>
    </div>
  );
}
