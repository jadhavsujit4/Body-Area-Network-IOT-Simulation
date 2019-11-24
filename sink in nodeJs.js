const axios = require('axios');

var PORT = 2356;
//var PORT = 33333;
//var HOST = '127.0.0.1';
var HOST = '0.0.0.0'

var dgram = require('dgram');
var server = dgram.createSocket('udp4');

server.on('listening', function() {
  var address = server.address();
 console.log('UDP Server listening on ' + address.address + ':' + address.port);
});

server.on('message', function(message, remote) {
   handle_udp_message(message, remote.port, remote.address);
   console.log(remote.address + ':' + remote.port +' - ' + message);
   console.log('Received %d bytes from %s:%d\n',message.length, remote.address, remote.port);
});

server.bind(PORT, HOST);

var threshold = 25;
var message_buffer_array = new Array(256);
for (var i = 0; i < message_buffer_array.length; i++) {
	message_buffer_array[i] = new Array();
}

function handle_udp_message(message, sender_port, sender_address){

	var dateobj = new Date();
	var device = message[0];
	var second_line = message[1];
	
	return_values = split_bits(second_line);

	w_flag  = return_values[0];
	r_flag = return_values[1];
	a_flag = return_values[2];
	power = return_values[3];

	var info_array = [message[2], message[3],message[4], message[5],message[6], message[7],message[8], message[9]];

	ack_packet = create_short_acknowledgement(device, w_flag, r_flag, a_flag, power);

	server.send(ack_packet,sender_port,sender_address,function(error){
  		if(error){
    					client.close();
  		}else{
    			console.log('Data sent !!!');
 	    }
 	})	

	binary_long_values = hex_decimal_float(info_array);
    info = long_binary_to_float(binary_long_values);

	console.log('Time:', dateobj.toISOString(),'Device:', device,'W:', w_flag, 'R:', r_flag, 'A:', a_flag, 'Power:', power, 'Info:', info);

	var save_string = '"'+dateobj.toISOString()+'":{"power":'+ power +',"warning":'+w_flag.toString()+',"data":'+info+'}'
	console.log(save_string);
	message_buffer_array[device-1].push(save_string);

	if(total_length(message_buffer_array)>threshold || (w_flag)){
		create_json(message_buffer_array);
		for (var i = 0; i < message_buffer_array.length; i++) {
			message_buffer_array[i] = new Array();
		}
	}
	
}	

function split_bits(decimal){
	//convert the input decimal to binary and then split later
	var power_level = 0;
    var binary = decimal_to_binary(decimal);
    for (var i = binary.length-1; i > 2; i--) {
    	power_level = power_level + (binary[i]*(Math.pow(2, 7-i)));
    	//console.log(binary[8-i],i-1);
    }
    return_array = [Boolean(binary[0]), Boolean(binary[1]), Boolean(binary[2]),power_level];
    return return_array;
}

// take in an array 0f 8 decimals (64-bits) and convert to array of 64 bits of binary digits
function hex_decimal_float(decimal_array){
	total_binary = [];
	for (var i = decimal_array.length-1; i >-1; i--) {
		var binary_array = decimal_to_binary(decimal_array[i]);
		total_binary = total_binary.concat(binary_array);
	}
    return total_binary;
}

// take in a decimal and convert to array of 8 binary digits
function decimal_to_binary(decimal){
	var binary = new Array(8)
	for (var i = binary.length - 1; i >= 0; i--) {
	 	binary[i] = decimal%2;
	 	decimal = parseInt(decimal/2);
	}
    return binary;
}

function long_binary_to_float(long_binary_array){
	float_value = 0;
	mantissa_value = 0;

	exponent_array = long_binary_array.slice(1,12);
	mantissa_array = long_binary_array.slice(12,64);

	exponent_value = binary_to_decimal(exponent_array);
	if (exponent_value==0) {exponent_flag=0;} else {exponent_flag=1;}
	final_exponent = Math.pow(2, exponent_value-1023);

	for (var i = 0; i < mantissa_array.length; i++) {
		mantissa_value = mantissa_value + (mantissa_array[i]*Math.pow(2,-i-1));
	}
    if (long_binary_array[0]==0) {sign=1;} else {sign=-1;}
	float_value = sign*final_exponent*(exponent_flag + mantissa_value);
	return float_value;
}

// take in an array of binary digits and return the decimal value
function binary_to_decimal(binary_array){
	decimal = 0;
	for (var i = 0; i < binary_array.length; i++) {
    	decimal = decimal + (binary_array[binary_array.length-1-i]*(Math.pow(2, i)));
    }
    return decimal;
}


function total_length(array){
	length = 0;
	for (var i = 0; i < array.length; i++) {
		length = length + array[i].length;
	}
	return length;
}

function create_json(filled_array){
	var json = '{';
	for (var i = 0; i < filled_array.length; i++) {
		//if(filled_array[i].length>0){
			json = json + '"device'+(i+1) + '":{'
				for (var j = 0; j < filled_array[i].length; j++) {
					if (j!=filled_array[i].length-1 && filled_array[i].length>1) {
						json = json + filled_array[i][j] + ',';
					}
					else {
						json = json + filled_array[i][j]
					}
				}
			if (i!=filled_array.length-1 && filled_array.length>1) {
				json = json + '},'
			}
			else {
				json = json + '}'
			}
		//}	
	}
	json = json + '}';
	console.log(json);
	axios.post('http://3.84.114.240:5000/post_data', json)
       .then(function (response) {
    			console.log(response);
  		})
  		.catch(function (error) {
    			console.log(error);
  		});
}
function create_short_acknowledgement(device, w_flag, r_flag, a_flag, power){
	var binary_array = new Array(8);
	if (w_flag){binary_array[0]=1} else{binary_array[0]=0}
	if (r_flag){binary_array[1]=1} else{binary_array[1]=0}
	binary_array[2]=1;
	for (var i = 7; i>2; i--) {
	 	binary_array[i] = power%2;
	 	power = parseInt(power/2);
	}
	var respone = device.toString() + String.fromCharCode(binary_to_decimal(binary_array));
	console.log(respone);
	return respone;
}