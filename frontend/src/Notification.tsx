import { toast } from "react-toastify";

type NotificationProps = {
  message: string;
  type: "info" | "success" | "error";
};

const Notification = ({ message, type }: NotificationProps) => {
  // if notification exists, dont create new one
  if (
    document.getElementsByClassName(
      "Toastify__toast Toastify__toast-theme--light Toastify__toast--error"
    ).length > 0
  ) {
    return;
  }

  switch (type) {
    case "info":
      toast.info(message, { autoClose: 3000, pauseOnHover: false });
      break;
    case "success":
      toast.success(message, { autoClose: 3000, pauseOnHover: false });
      break;
    case "error":
      toast.error(message, { autoClose: 3000, pauseOnHover: false });
      break;
    default:
      toast.info(message, { autoClose: 3000, pauseOnHover: false });
      break;
  }
};

export default Notification;
