_template = """
/*
 * This is a template-generated file from BoneScript
 */

/dts-v1/;
/plugin/;

/{
    compatible = "ti,beaglebone", "ti,beaglebone-black";
    part_number = "BS_PINMODE____PIN_KEY_______DATA___";

    exclusive-use =
        "___PIN_DOT_KEY___",
        "___PIN_FUNCTION___";

    fragment@0 {
        target = <&am33xx_pinmux>;
        __overlay__ {
            bs_pinmode____PIN_KEY_______DATA___: pinmux_bs_pinmode____PIN_KEY_______DATA___ {
                pinctrl-single,pins = <___PIN_OFFSET___ ___DATA___>;
            };
        };
    };

    fragment@1 {
        target = <&ocp>;
        __overlay__ {
            bs_pinmode____PIN_KEY_______DATA____pinmux {
                compatible = "bone-pinmux-helper";
                status = "okay";
                pinctrl-names = "default";
                pinctrl-0 = <&bs_pinmode____PIN_KEY_______DATA___>;
            };
        };
    };
};
"""