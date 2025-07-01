if exploration_mode:
            direction = "DON (CIZGI ARANIYOR)"

        stable_direction = get_stable_direction(direction)

        x1, y1, x2, y2 = scaled_joystick_value(stable_direction, orientation_angle, cx_offset)
        send_joystick_values(x1, y1, x2, y2)
        read_motor_values()

        cv2.putText(frame, f"Yon: {stable_direction}", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        if orientation_angle is not None:
            cv2.putText(frame, f"Aci: {int(orientation_angle)}", (30, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
        cv2.putText(frame, f"X1:{x1} Y1:{y1} X2:{x2} Y2:{y2}", (30, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 200, 200), 2)
        cv2.rectangle(frame, (roi_left, roi_top), (roi_right, roi_bottom), (255, 0, 0), 2)

        cv2.imshow("Line Following", frame)
        cv2.imshow("ROI Mask", mask_roi)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    picam2.close()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    line_following()
