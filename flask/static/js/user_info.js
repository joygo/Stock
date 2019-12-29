
import { getUsefulContents } from './functions.js';
import { formatParams } from './functions.js';

(function(document) {
	'use strict';

	var stock_name = new Array();
	var stock_number = new Array();

    var LightTableFilter = (function(Arr) {

		var _input;

		// 資料輸入事件處理函數
		function _onInputEvent(e) {
			_input = e.target;
			var tables = document.getElementsByClassName(_input.getAttribute('data-table'));
			Arr.forEach.call(tables, function(table) {
			Arr.forEach.call(table.tBodies, function(tbody) {
				Arr.forEach.call(tbody.rows, _filter);
			});
			});
		}

		// 資料篩選函數，顯示包含關鍵字的列，其餘隱藏
		function _filter(row) {
			var text = row.textContent.toLowerCase(), val = _input.value.toLowerCase();
			row.style.display = text.indexOf(val) === -1 ? 'none' : 'table-row';
		}

		return {
			// 初始化函數
			init: function() {
			var inputs = document.getElementsByClassName('light-table-filter');
			Arr.forEach.call(inputs, function(input) {
				input.oninput = _onInputEvent;
			});
			}
		};
	})(Array.prototype);

    function waitUI() {
		$.blockUI({
			message: ' Loading ....',
			// message: '<h1><img src="./../static/images/loading.gif" />',
			css: {
				height: '50px',
				color: '#3498db'

			}
		});
		// alert("程式執行中");//主程式，這裡用alert代替
	}

	function autocomplete_func(error_code, data, des, status)
	{
		stock_name = data['stock_name'];
		stock_number = data['stock_number'];
		$("#buy_stock_name").autocomplete({
			source: stock_name
		});
		$( "#buy_stock_name" ).autocomplete( "option", "appendTo", ".modal-body" );

		$("#buy_stock_number").autocomplete({
			source: stock_number
		});
		$( "#buy_stock_number" ).autocomplete( "option", "appendTo", ".modal-body" );

		$("#sell_stock_name").autocomplete({
			source: stock_name
		});
		$( "#sell_stock_name" ).autocomplete( "option", "appendTo", "#sellStock .modal-body" );

		$("#sell_stock_number").autocomplete({
			source: stock_number
		});
		$( "#sell_stock_number" ).autocomplete( "option", "appendTo", "#sellStock .modal-body" );

	}

    function InitUi() {
		// $("#data_table").tablesorter();



		$("#buy_stock_name").on('click', function(){

			var buyStockNumber = $("#buy_stock_number").val();
			if(buyStockNumber)
			{
				var index = stock_number.indexOf(buyStockNumber);
				console.log(stock_name[index]);
				if(stock_name[index])
				{
					$("#buy_stock_name").val(stock_name[index]);
				}
			}
		});

		$("#buy_stock_number").on('click', function(){

			var buyStockName = $("#buy_stock_name").val();
			if(buyStockName)
			{
				var index = stock_name.indexOf(buyStockName);
				console.log(stock_name[index]);
				if(stock_number[index])
				{
					$("#buy_stock_number").val(stock_number[index]);
				}
			}
		});

		$("#sell_stock_name").on('click', function(){

			var sellStockNumber = $("#sell_stock_number").val();
			if(sellStockNumber)
			{
				var index = stock_number.indexOf(sellStockNumber);
				if(stock_name[index])
				{
					$("#sell_stock_name").val(stock_name[index]);
				}
			}
		});

		$("#sell_stock_number").on('click', function(){

			var sellStockName = $("#sell_stock_name").val();
			if(sellStockName)
			{
				var index = stock_name.indexOf(sellStockName);
				if(stock_number[index])
				{
					$("#sell_stock_number").val(stock_number[index]);
				}
			}
		});

		if(stock_number.length==0 || stock_name.length==0)
		{
			var url = "http://127.0.0.1:5000/api/add_info"
			getUsefulContents(url, "GET", "", data => { post_callback(data, autocomplete_func) });

		}

		// default sort by stock count
		$('#data_table').DataTable({
			"order": [[5, "desc"]]
		});
		$('#buy_data_table').DataTable();
		$('#sell_data_table').DataTable();

		$( "#buy_start_datepicker" ).datepicker({
			// http://www.runoob.com/jqueryui/example-datepicker.html
			changeMonth: true,
			changeYear: true,
			dateFormat: "yymmdd",
			onSelect : function(dateText, inst){
				(dateText);
			}

    	  });
		$( "#sell_start_datepicker" ).datepicker({
			// http://www.runoob.com/jqueryui/example-datepicker.html
			changeMonth: true,
			changeYear: true,
			dateFormat: "yymmdd",
			onSelect : function(dateText, inst){
				(dateText);
			}

    	  });
      	$( "#buy_end_datepicker" ).datepicker({
			// http://www.runoob.com/jqueryui/example-datepicker.html
			changeMonth: true,
			changeYear: true,
			dateFormat: "yymmdd",
			onSelect : function(dateText, inst){
			alert(dateText);
			}

     	 });
      	$( "#sell_end_datepicker" ).datepicker({
			// http://www.runoob.com/jqueryui/example-datepicker.html
			changeMonth: true,
			changeYear: true,
			dateFormat: "yymmdd",
			onSelect : function(dateText, inst){
			alert(dateText);
			}

     	 });

      	$( "#buy_datepicker" ).datepicker({
			// http://www.runoob.com/jqueryui/example-datepicker.html
			changeMonth: true,
			changeYear: true,
			dateFormat: "yymmdd",
			onSelect : function(dateText, inst){
				console.log(dateText.substring(0,4))
				console.log(dateText.substring(4,6))
				console.log(dateText.substring(6,8))
				var date = new Date(dateText.substring(0,4), parseInt(dateText.substring(4,6))-1, dateText.substring(6,8));
				var date1 = new Date();
				if(date > date1)
				{
					alert("日期有誤");
					$( "#buy_datepicker" ).datepicker('setDate', null);
				}
			}

    	  });

      	$( "#sell_datepicker" ).datepicker({
			// http://www.runoob.com/jqueryui/example-datepicker.html
			changeMonth: true,
			changeYear: true,
			dateFormat: "yymmdd",
			onSelect : function(dateText, inst){
				console.log(dateText.substring(0,4))
				console.log(dateText.substring(4,6))
				console.log(dateText.substring(6,8))
				var date = new Date(dateText.substring(0,4), parseInt(dateText.substring(4,6))-1, dateText.substring(6,8));
				var date1 = new Date();
				if(date > date1)
				{
					alert("日期有誤");
					$( "#sell_datepicker" ).datepicker('setDate', null);
				}
			}

     	 });

		$('#buyStock').on('show.bs.modal', function (event) {
			var button = $(event.relatedTarget) // Button that triggered the modal
			var recipient = button.data('whatever') // Extract info from data-* attributes
			// If necessary, you could initiate an AJAX request here (and then do the updating in a callback).
			// Update the modal's content. We'll use jQuery here, but you could use a data binding library or other methods instead.

			var modal = $(this)
			modal.find('.modal-title').text(recipient)
			// modal.find('.modal-body input').val(recipient)
			});

        $('#buyStock').on('click', '.modal-footer .btn-primary',function (event) {
          	var input_data = new Object();
			$("#buyStock").find('input').each(function(){
				var name = $(this).attr('name');
				var val = $(this).val();
				input_data[name] = val;
			})
			input_data["action"] = "buy";
			input_data["user"] = localStorage.getItem("user_name");
			var url = "http://127.0.0.1:5000/api/add_info";
			getUsefulContents(url, "POST", input_data, data => { post_callback(data); });


		});

		$('#sellStock').on('click', '.modal-footer .btn-primary',function (event) {

			var input_data = new Object();
			$("#sellStock").find('input').each(function(){
					var name = $(this).attr('name');
					var val = $(this).val();
					input_data[name] = val;
			})
			input_data["action"] = "sell";
			input_data["user"] = localStorage.getItem("user_name");


			var url = "http://127.0.0.1:5000/api/add_info";
			getUsefulContents(url, "POST", input_data, data => { post_callback(data); });

		});

		$('#update_db_btn').on('click',function (event)
		{
			// var values = new Array();
			// $.each($("input[name='case[]']:checked"), function(){
			// 	var data = $(this).parents('tr:eq(0)');
			// 	values.push({
			// 		'stock_name': $(data).find('td:eq(1)').text(),
			// 		'stock_date': $(data).find('td:eq(6)').text(),
			// 	});

			// })
			var test;
			// test = $("#data_table tr th:nth-child(7)").html("實現損益(含股利)");
			var url = "http://127.0.0.1:5000/api/update_db"
			getUsefulContents(url, "GET", "", data => { });
		});

		$('#btn_test').on('click',function (event)
		{
			// var values = new Array();
			// $.each($("input[name='case[]']:checked"), function(){
			// 	var data = $(this).parents('tr:eq(0)');
			// 	values.push({
			// 		'stock_name': $(data).find('td:eq(1)').text(),
			// 		'stock_date': $(data).find('td:eq(6)').text(),
			// 	});

			// })
			var test;
			// test = $("#data_table tr th:nth-child(7)").html("實現損益(含股利)");
			$("#fee_count").val("0");
			console.log(test);

		});

		$('#btn_delete_buy').on('click',function (event)
		{
			var input_data = new Object();
			var values = getCheckInfo("buy");
			input_data['user'] = localStorage.getItem('user_name');
			input_data['data'] = values;
			var url = "http://127.0.0.1:5000/api/add_info"
			getUsefulContents(url, "DELETE", input_data, data => { post_callback(data); });

			// console.log(json_data);

		});

		$('#btn_delete_sell').on('click',function (event)
		{
			var input_data = new Object();
			var values = getCheckInfo("sell");
			input_data['user'] = localStorage.getItem('user_name');
			input_data['data'] = values;
			var url = "http://127.0.0.1:5000/api/add_info"
			getUsefulContents(url, "DELETE", input_data, data => { post_callback(data); });

			// console.log(json_data);

		});

		$('#btnUserConfig').on('click',function (event)
		{
			var input_data = new Object();
			// var values = getCheckInfo("config");
			input_data['user'] = localStorage.getItem('user_name');
			// input_data['data'] = values;
			// var url = "http://127.0.0.1:5000/api/add_info"
			// getUsefulContents(url, "DELETE", input_data, data => { post_callback(data); });
			var data = new Object();
			$('input[name="div"]').each(function(){

				// values.push($(this).val());
				if($(this).is(':checked'))
				{
					data[$(this).val()] = "1";
				}
				else
				{
					data[$(this).val()] = "0";
				}

			});

			$('input[name="fee"]').each(function(){

				data[$(this).attr("ID")] = $(this).val()


			});
			console.log(data);
			input_data['data'] = data;
			var url = "http://127.0.0.1:5000/user"
			getUsefulContents(url, "POST", input_data, data => { post_callback(data); });

		});


	}

	function getCheckInfo(target)
	{
		var values = new Array();
		$.each($("input[name='case[]']:checked"), function(){
			var data = $(this).parents('tr:eq(0)');
			values.push({
				'stock_name': $(data).find('td:eq(1)').text(),
				'target': target,
				'date': $(data).find('td:eq(6)').text(),
			});

		})

		return values;

	}
	function test_function(error_code, data, des, status)
	{
		if( error_code == "0" )
		{
			// alert("成功~~");
			// window.location.href = "http://127.0.0.1:5000/user";
		}
		else
		{
			alert(des);
		}
	}

	function update_polling_datas(error_code, data, des, status)
	{
		var update_db_date = "";
		if( error_code == "0" )
		{
			$.each(data, function(key, value){
				if( key == "update_db_date")
				{
					update_db_date = value;
					$("#db_version").html(update_db_date);
				}
			})
		}
		else
		{
			alert(des);
		}
	}


	function post_callback(return_data, func=null) {
		var error_code = "";
		var data;
		var des = "";
		var status = "";

		$.each(return_data, function(key, value){
			if( key == "error")
			{
				error_code = value;
			}
			else if( key == "data")
			{
				data = value;
			}
			else if( key == "status")
			{
				status = value;
			}
			else if( key == "des")
			{
				des = value;
			}
		});

		if(func != null)
		{
			func(error_code, data, des, status);
		}
		else
		{
			if( error_code == "0" )
			{
				// alert("成功");
				window.location.href = "http://127.0.0.1:5000/user";
			}
			else
			{
				alert(des);
			}
		}
	}



	function show_user_info(data)
	{
		var myObject = data
		var income = "";
		var cost = "";
		var buy_date = "";
		var buy_count = "";
		var today_price = "";
		var unsell_income  = "";
		var buy_price = "";
		var sell_date = "";
		var sell_count = "";
		var sell_price = "";
		var sell_income = "";
		var all_unsell_income  = 0;
		var all_income = 0;
		var all_now_cost = 0;
		var summary_cost = 0;
		var summary_price = 0;
		var summary_count = 0;
		var stock_number  = "";
        if(myObject['error'] == "0")
        {
			myObject['data'].forEach(function(object)
			{

				if(object['buy'] != undefined)
				{
					$.each(object['buy'], function(key, value)
					{
								// console.log("key = " +key+", value = " + value);
						income = "0";
						cost = "";
						buy_date = "";
						buy_count = "";
						buy_price = "";

						$.each(value, function(option, data)
						{
							data = String(data);

							if(option == "投資成本")
							{
								if(data)
								{
									cost = data.split(",");
								}
							}
							else if(option == "購買時間")
							{
								if(data)
								{
									buy_date = data.split(",");
								}
							}
							else if(option == "購買數量")
							{
								if(data)
								{
									buy_count = data.split(",");
								}
							}
							else if(option == "購買股價")
							{
								if(data)
								{
									buy_price = data.split(",");
								}
							}
							else if(option == "股票代號")
							{
								if(data)
								{
									stock_number = data;
								}
							}

						});
						for(var i = 0; i < buy_count.length; i++)
						{
							$("#buy_data_table").DataTable().row.add([
								'<input type="checkbox" name="case[]"></input>',
								key,
								stock_number,
								cost[i],
								buy_price[i],
								buy_count[i],
								buy_date[i]
								] ).draw( false );
						}
					});
				}
				else if(object['sell'] != undefined)
				{
					console.log(object['sell']);
					$.each(object['sell'], function(key, value)
					{
								// console.log("key = " +key+", value = " + value);
						income = "0";
						cost = "";
						sell_income = "";
						sell_date = "";
						sell_count = "";
						sell_price = "";
						$.each(value, function(option, data)
						{
							data = String(data);
							if(option == "賣出股價")
							{
								if(data)
								{
									sell_price = data.split(",");
								}
							}
							else if(option == "賣出價格")
							{
								if(data)
								{
									sell_income = data.split(",");
								}
							}
							else if(option == "賣出時間")
							{
								if(data)
								{
									sell_date = data.split(",");
								}
							}
							else if(option == "賣出數量")
							{
								if(data)
								{
									sell_count = data.split(",");
								}
							}
							else if(option == "股票代號")
							{
								if(data)
								{
									stock_number = data;
								}
							}
							else if(option == "實現損益")
							{
								if(data)
								{
									income = data.split(",");
								}
							}
							else if(option == "購買成本")
							{
								if(data)
								{
									cost = data.split(",");
								}
							}


							});
							for(var i = 0; i < sell_count.length; i++)
							{
								$("#sell_data_table").DataTable().row.add([
									'<input type="checkbox" name="case[]"></input>',
									key,
									stock_number,
									sell_income[i],
									sell_price[i],
									sell_count[i],
									sell_date[i],
									income[i],
									cost[i]
									] ).draw( false );
							}
					});

				}
				else if(object['summary'] != undefined)
				{
					console.log(object['summary']);
					$.each(object['summary'], function(key, value)
					{
								// console.log("key = " +key+", value = " + value);
						income = "0";
						cost = "";
						buy_date = "";
						buy_count = "";
						buy_price = "";
						today_price = 0;
						summary_cost = 0;
						summary_price = 0;
						summary_count = 0;
						unsell_income = 0;
						stock_number = "";

						$.each(value, function(option, data)
						{
							// console.log("option = " +option+", value = " + value);
							data = String(data);
							if(option == "實現損益")
							{
								income = data;
								all_income = all_income + parseFloat(income);

							}
							else if(option == "投資成本")
							{
								if(data)
								{
									cost = data.split(",");
								}
							}
							else if(option == "購買時間")
							{
								if(data)
								{
									buy_date = data.split(",");
								}
							}
							else if(option == "購買數量")
							{
								if(data)
								{
									buy_count = data.split(",");
								}
							}
							else if(option == "購買股價")
							{
								if(data)
								{
									buy_price = data.split(",");
								}
							}
							else if(option == "股票代號")
							{
								if(data)
								{
									stock_number = data;
								}
							}
							else if(option == "今日股價")
							{
								if(data)
								{
									today_price = data;
								}
							}
							else if(option == "未實現損益")
							{
								if(data)
								{
									unsell_income = parseInt(data);
								}
							}


							});
							if(buy_count)
							{

								for(var i = 0; i < buy_count.length; i++)
								{


									summary_cost = summary_cost + parseInt(cost[i]);
									summary_price = summary_price + parseFloat(buy_price[i])*parseInt(buy_count[i]);
									summary_count = summary_count + parseInt(buy_count[i]);

								}
								all_unsell_income = all_unsell_income + unsell_income;
								all_now_cost  = all_now_cost + summary_cost;
								console.log(summary_cost, summary_price, summary_count, all_now_cost, all_unsell_income);
							}
							var unsell_income_str = ""
							if (unsell_income > 0)
							{
								unsell_income_str = String(unsell_income) + "  (" + String((unsell_income*100/summary_cost).toFixed(2))  + "%)";
							}
							else
							{
								unsell_income_str = String(unsell_income)
							}
							console.log("usell_income = " + unsell_income_str);
							$("#data_table").DataTable().row.add([
								key,
								stock_number,
								String(summary_cost),
								(summary_count > 0) ? Math.round(summary_price/summary_count*100)/100: summary_price,
								String(today_price),
								summary_count,
								income,
								unsell_income_str
								] ).draw( false );

						});
					$("#all_income").append(String(all_income));
					$("#all_now_cost").append(String(all_now_cost));
					$("#all_unsell_income").append(String(all_unsell_income));
				}
				else if(object['user_config'] != undefined)
				{
					$.each(object['user_config'], function(key, value)
					{
						console.log(key);

						switch (key)
						{
							case "dividend_price":
								if(value == "1")
								{
									$('#'+key).prop('checked', true);
									$("#data_table tr th:nth-child(7)").html("實現損益(含股利)");
								}
								else
								{
									$('#'+key).prop('checked', false);
								}
								break;
							case "dividend_stock":
								if(value == "1")
								{
									$('#'+key).prop('checked', true);
									$("#data_table tr th:nth-child(7)").html("實現損益(含股利)");
								}
								else
								{
									$('#'+key).prop('checked', false);
								}
								break;
							case "handing_fee":
								$('#'+key).val(value);
								break;

							case "fee_count":
								$('#'+key).val(value);
								console.log(value);
								break;
						}



					});
				}
			});


        };
        // $("#all_income").append(String(all_income));




    }


    // 網頁載入完成後，啟動 LightTableFilter
    document.addEventListener('readystatechange', function() {
      if (document.readyState === 'complete') {
		waitUI();

        InitUi();
        console.log(localStorage.getItem("user_name"));
        var data = new Object();
        data.user = localStorage.getItem("user_name")
        var url = "http://127.0.0.1:5000/api/get_info" +formatParams(data);
        getUsefulContents(url , 'GET', "", data => { show_user_info(data); });
        // var xhttp = new XMLHttpRequest();
        // xhttp.open("POST", "http://127.0.0.1:5000/user", false);
        // xhttp.send();
        // // waitUI();
		// $.unblockUI();
        // var data = xhttp.responseText;
		setTimeout($.unblockUI, 500);

		// set polling
		var poolling_function = setInterval( function(){
			var url = "http://127.0.0.1:5000/api/polling"
			getUsefulContents(url, "GET", "", data => { post_callback(data, update_polling_datas) });

		}, 10000);

        LightTableFilter.init();
      }

    });





  })(document);